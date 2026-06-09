let allComponents = [];

function renderComponentBadges() {
    const container = document.getElementById('componentBadges');
    if (!container) return;
    
    container.innerHTML = '';
    allComponents.forEach(comp => {
        const badge = document.createElement('button');
        badge.className = 'component-badge';
        badge.innerHTML = `${comp.name}<span class="component-count">${comp.count}</span>`;
        container.appendChild(badge);
    });
}

// Load components first
fetch('./components.json')
    .then(response => response.json())
    .then(data => {
        allComponents = data.components || [];
        renderComponentBadges();
    })
    .catch(err => {
        console.error('Failed to load components:', err);
    });

// Load posts separately
fetch('./en_posts/index.json')
    .then(response => response.json())
    .then(data => {
        const grid = document.getElementById('postsGrid');
        data.slice(0, 12).forEach(post => {
            const cardNum = post.directory.split('_')[0];
            const postEl = document.createElement('article');
            postEl.className = 'post-card';
            postEl.innerHTML = `
                <div class="post-card-header">#${cardNum}</div>
                <div class="post-card-content">
                    <h3><a href="./en_posts/${post.directory}/content.html">${post.title}</a></h3>
                    <div class="post-card-meta">
                        <span>📅 ${post.publish_date || 'Date unknown'}</span>
                        <span>📖 Article ${cardNum}</span>
                    </div>
                    <div class="post-card-excerpt">
                        ${post.original_title}
                    </div>
                    <div class="post-card-footer">
                        <div class="post-tags">
                            <span class="tag">Read</span>
                        </div>
                        <a href="./en_posts/${post.directory}/content.html" class="read-link">Read More →</a>
                    </div>
                </div>
            `;
            grid.appendChild(postEl);
        });
    })
    .catch(err => {
        console.error('Failed to load posts:', err);
        document.getElementById('postsGrid').innerHTML = '<p style="color: white;">No translated posts available yet.</p>';
    });
