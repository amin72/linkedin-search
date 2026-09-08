const API_BASE = 'http://localhost:8000/api';

let currentPage = 1;
let totalPages = 1;
const PAGE_SIZE = 10;

$(document).ready(function() {
    console.log('🚀 App loaded');
    loadFilters();
    performSearch(1);
});

function loadFilters() {
    console.log('📡 Loading filters...');
    $.ajax({
        url: API_BASE + '/filters',
        method: 'GET',
        success: function(data) {
            console.log('✅ Filters loaded:', data);
            const $skill = $('#skillFilter');
            const $title = $('#titleFilter');

            $skill.empty().append('<option value="">All Skills</option>');
            if (data.skills && data.skills.length > 0) {
                data.skills.forEach(function(s) {
                    $skill.append('<option value="' + s + '">' + s + '</option>');
                });
            }

            $title.empty().append('<option value="">All Titles</option>');
            if (data.titles && data.titles.length > 0) {
                data.titles.forEach(function(t) {
                    $title.append('<option value="' + t + '">' + t + '</option>');
                });
            }
        },
        error: function() {
            console.error('❌ Failed to load filters');
        }
    });
}

function performSearch(page) {
    page = page || 1;

    const q = $('#searchInput').val().trim();
    const skill = $('#skillFilter').val();
    const title = $('#titleFilter').val();

    currentPage = page;

    console.log('🔍 Searching:', { q, skill, title, page });

    $('#loadingIndicator').show();
    $('#resultsContainer').html('');
    $('#pagination').html('');
    $('#resultCount').text('Searching...');

    $.ajax({
        url: API_BASE + '/search',
        method: 'GET',
        data: {
            q: q,
            skill: skill,
            title: title,
            page: page,
            page_size: PAGE_SIZE
        },
        success: function(response) {
            console.log('✅ API Response:', response);
            console.log('📄 Total pages:', response.total_pages);

            $('#loadingIndicator').hide();

            totalPages = response.total_pages || 1;
            $('#resultCount').text(response.total + ' profiles found');

            if (response.results && response.results.length > 0) {
                renderResults(response.results);
                console.log('📄 Calling renderPagination with:', response.page, response.total_pages);
                renderPagination(response.page, response.total_pages);
            } else {
                showNoResults();
            }
        },
        error: function(xhr, status, error) {
            $('#loadingIndicator').hide();
            console.error('❌ Search error:', error);
            $('#resultsContainer').html(`
                <div class="no-results">
                    <h3>⚠️ Error loading results</h3>
                    <p>Please check that the backend is running at ${API_BASE}</p>
                    <p style="font-size:0.8rem;color:var(--muted-color);">Error: ${error}</p>
                </div>
            `);
            $('#pagination').html('');
        }
    });
}

function renderResults(results) {
    console.log('🎨 Rendering', results.length, 'results');
    let html = '';

    results.forEach(function(p) {
        const name = p.full_name || p.first_name + ' ' + p.last_name || 'Unknown';

        const locationParts = [
            p.location_locality,
            p.location_region,
            p.location_country
        ].filter(Boolean);
        const location = p.location_name || locationParts.join(', ') || 'Not specified';

        const skills = (p.skills || []).filter(function(s) {
            return s && s.trim();
        });

        const skillTags = skills.slice(0, 10).map(function(s) {
            return '<span class="skill-tag">' + s + '</span>';
        }).join('');
        const moreSkills = skills.length > 10 ? '<span class="skill-tag">+' + (skills.length - 10) + ' more</span>' : '';

        let linkedinUrl = p.linkedin_url || (p.linkedin_username ? 'linkedin.com/in/' + p.linkedin_username : '');
        if (linkedinUrl && !linkedinUrl.startsWith('http')) {
            linkedinUrl = 'https://www.' + linkedinUrl;
        }

        let summary = p.summary;
        if (Array.isArray(summary)) {
            const cleaned = summary.filter(function(s) {
                return s && s.trim();
            });
            summary = cleaned.length > 0 ? cleaned.join(' ') : '';
        }
        if (typeof summary === 'string') {
            summary = summary.trim();
        } else {
            summary = '';
        }
        if (summary.length > 200) {
            summary = summary.substring(0, 200) + '...';
        }

        html += `
            <div class="profile-card">
                <div class="profile-name">${name}</div>
                <div class="profile-job">
                    ${p.job_title || 'No title specified'}
                    ${p.job_company_name ? '<span class="profile-company">@ ' + p.job_company_name + '</span>' : ''}
                </div>
                <div class="profile-location">
                    <span class="label">Location:</span> ${location}
                </div>
                ${skillTags ? '<div class="profile-skills"><span class="label">Skills:</span> ' + skillTags + moreSkills + '</div>' : ''}
                ${summary ? '<div class="profile-summary"><span class="label">Summary:</span> ' + summary + '</div>' : ''}
                ${linkedinUrl ? '<div class="profile-link"><span class="label">Profile:</span> <a href="' + linkedinUrl + '" target="_blank">LinkedIn</a></div>' : ''}
            </div>
        `;
    });

    $('#resultsContainer').html(html);
}

function renderPagination(currentPage, totalPages) {
    console.log('🔥 renderPagination called with:', { currentPage, totalPages });

    if (!totalPages || totalPages <= 1) {
        console.log('⚠️ No pagination needed (totalPages <= 1)');
        $('#pagination').html('');
        return;
    }

    let html = '';

    html += '<button ' + (currentPage === 1 ? 'disabled' : '') + ' data-page="' + (currentPage - 1) + '">Previous</button>';

    if (currentPage > 3) {
        html += '<button data-page="1">1</button>';
        if (currentPage > 4) {
            html += '<button disabled>…</button>';
        }
    }

    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);

    for (var i = startPage; i <= endPage; i++) {
        html += '<button class="' + (i === currentPage ? 'active' : '') + '" data-page="' + i + '" ' + (i === currentPage ? 'disabled' : '') + '>' + i + '</button>';
    }

    if (currentPage < totalPages - 2) {
        if (currentPage < totalPages - 3) {
            html += '<button disabled>…</button>';
        }
        html += '<button data-page="' + totalPages + '">' + totalPages + '</button>';
    }

    html += '<button ' + (currentPage === totalPages ? 'disabled' : '') + ' data-page="' + (currentPage + 1) + '">Next</button>';

    console.log('📄 Pagination HTML:', html);
    $('#pagination').html(html);

    $('#pagination button[data-page]').on('click', function() {
        if (!$(this).attr('disabled')) {
            var page = parseInt($(this).data('page'));
            console.log('🔄 Navigating to page:', page);
            performSearch(page);
            $('html, body').animate({
                scrollTop: $('#resultsSection').offset().top - 100
            }, 300);
        }
    });
}

function showNoResults() {
    $('#resultsContainer').html(`
        <div class="no-results">
            <h3>🔍 No profiles found</h3>
            <p>Try adjusting your search terms or filters.</p>
        </div>
    `);
    $('#pagination').html('');
}

// Event handlers
$('#searchForm').on('submit', function(e) {
    e.preventDefault();
    console.log('📝 Form submitted');
    performSearch(1);
});

$('#searchInput').on('keypress', function(e) {
    if (e.which === 13) {
        e.preventDefault();
        console.log('📝 Enter key pressed');
        performSearch(1);
    }
});

$('#clearFilters').on('click', function() {
    console.log('🧹 Clearing filters');
    $('#searchInput').val('');
    $('#skillFilter').val('');
    $('#titleFilter').val('');
    performSearch(1);
});

$('#skillFilter, #titleFilter').on('change', function() {
    console.log('📝 Filter changed');
    performSearch(1);
});