const POSTS_PER_PAGE = 12;
let allPosts = [];
let allComponents = [];
let currentCategory = 'All';
let selectedComponents = new Set();
let currentPage = 1;

function renderComponentBadges() {
    const container = document.getElementById('componentBadges');
    container.innerHTML = '';

    allComponents.forEach(comp => {
        const badge = document.createElement('button');
        badge.className = 'component-badge';
        if (selectedComponents.has(comp.name)) {
            badge.classList.add('active');
        }
        badge.innerHTML = `${comp.name}<span class="component-count">${comp.count}</span>`;
        badge.addEventListener('click', () => {
            if (selectedComponents.has(comp.name)) {
                selectedComponents.delete(comp.name);
            } else {
                selectedComponents.add(comp.name);
            }
            currentPage = 1;
            renderComponentBadges();
            updateFilterInfo();
            filterAndRender();
        });
        container.appendChild(badge);
    });
}

function updateFilterInfo() {
    const info = document.getElementById('filterInfo');
    if (selectedComponents.size === 0) {
        info.textContent = '';
        return;
    }
    const components = Array.from(selectedComponents).join(', ');
    info.innerHTML = `🔍 Filtering by: <span>${components}</span>`;
}

function renderPagination(totalPosts) {
    const totalPages = Math.ceil(totalPosts / POSTS_PER_PAGE);
    const paginationDiv = document.getElementById('pagination');
    paginationDiv.innerHTML = '';

    if (totalPages <= 1) return;

    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.className = 'pagination-btn';
    prevBtn.textContent = '← Previous';
    prevBtn.disabled = currentPage === 1;
    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            filterAndRender();
            window.scrollTo(0, 0);
        }
    });
    paginationDiv.appendChild(prevBtn);

    // Page number buttons
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);

    if (startPage > 1) {
        const firstBtn = document.createElement('button');
        firstBtn.className = 'pagination-btn';
        firstBtn.textContent = '1';
        firstBtn.addEventListener('click', () => {
            currentPage = 1;
            filterAndRender();
            window.scrollTo(0, 0);
        });
        paginationDiv.appendChild(firstBtn);

        if (startPage > 2) {
            const dots = document.createElement('span');
            dots.style.color = 'white';
            dots.style.alignSelf = 'center';
            dots.textContent = '...';
            paginationDiv.appendChild(dots);
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.className = 'pagination-btn';
        if (i === currentPage) pageBtn.classList.add('active');
        pageBtn.textContent = i;
        pageBtn.addEventListener('click', () => {
            currentPage = i;
            filterAndRender();
            window.scrollTo(0, 0);
        });
        paginationDiv.appendChild(pageBtn);
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            const dots = document.createElement('span');
            dots.style.color = 'white';
            dots.style.alignSelf = 'center';
            dots.textContent = '...';
            paginationDiv.appendChild(dots);
        }

        const lastBtn = document.createElement('button');
        lastBtn.className = 'pagination-btn';
        lastBtn.textContent = totalPages;
        lastBtn.addEventListener('click', () => {
            currentPage = totalPages;
            filterAndRender();
            window.scrollTo(0, 0);
        });
        paginationDiv.appendChild(lastBtn);
    }

    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.className = 'pagination-btn';
    nextBtn.textContent = 'Next →';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            filterAndRender();
            window.scrollTo(0, 0);
        }
    });
    paginationDiv.appendChild(nextBtn);
}

function renderPosts(filteredPosts) {
    const grid = document.getElementById('postsGrid');
    grid.innerHTML = '';

    if (filteredPosts.length === 0) {
        grid.innerHTML = '<p style="color: white; grid-column: 1/-1;">No articles found for this category or technology.</p>';
        document.getElementById('pagination').innerHTML = '';
        return;
    }

    const startIdx = (currentPage - 1) * POSTS_PER_PAGE;
    const endIdx = startIdx + POSTS_PER_PAGE;
    const postsToShow = filteredPosts.slice(startIdx, endIdx);

    postsToShow.forEach(post => {
        const postEl = document.createElement('article');
        postEl.className = 'post-card';
        postEl.innerHTML = `
            <div class="post-card-header">#${String(post.id).padStart(4, '0')}</div>
            <div class="post-card-content">
                <div class="category-badge ${post.category}">
                    ${post.category}
                </div>
                <h3><a href="./en_post/${post.filename}">${post.title}</a></h3>
                <div class="post-card-meta">
                    <span>📅 ${post.publish_date || 'Unknown date'}</span>
                    <span>👁️ ${post.view_count} views</span>
                </div>
                <div class="post-card-excerpt">
                    <p>📖 ${post.read_time || 'Unknown read time'}</p>
                </div>
                <div class="post-card-footer">
                    <div class="post-tags">
                    </div>
                    <a href="./en_post/${post.filename}" class="read-link">Read more →</a>
                </div>
            </div>
        `;
        grid.appendChild(postEl);
    });

    renderPagination(filteredPosts.length);
}

function filterAndRender() {
    let filtered = allPosts;

    // Filter by category
    if (currentCategory !== 'All') {
        filtered = filtered.filter(post => post.category === currentCategory);
    }

    // Filter by components (if any selected)
    if (selectedComponents.size > 0) {
        filtered = filtered.filter(post => {
            const postComponents = post.components || [];
            return Array.from(selectedComponents).some(comp => 
                postComponents.includes(comp)
            );
        });
    }

    renderPosts(filtered);
}

// Load posts and components
Promise.all([
    fetch('./en_post/index.json').then(r => r.json()),
    fetch('./components.json').then(r => r.json())
]).then(([posts, components]) => {
    allPosts = posts;
    allComponents = components.components;

    renderComponentBadges();
    renderPosts(allPosts);

    // Set up category filter buttons
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCategory = btn.textContent.trim();
            currentPage = 1;
            filterAndRender();
        });
    });
}).catch(err => {
    console.error('Error loading data:', err);
    document.getElementById('postsGrid').innerHTML = '<p style="color: white;">Unable to load articles. Please make sure en_post/index.json and components.json exist.</p>';
});
