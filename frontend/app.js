async function fetchJobs() {
  const q = document.getElementById('q').value.trim();
  const tag = document.getElementById('tag').value;
  const location = document.getElementById('location').value.trim();

  const params = new URLSearchParams();
  if (q) params.set('q', q);
  if (tag) params.set('tag', tag);
  if (location) params.set('location', location);
  params.set('limit', '100');

  const res = await fetch('/jobs?' + params.toString());
  const data = await res.json();
  render(data.items || []);
}

function render(items) {
  const el = document.getElementById('list');
  if (!items.length) {
    el.innerHTML = '<p>Không có dữ liệu phù hợp.</p>';
    return;
  }
  el.innerHTML = items.map(i => `
    <article class="card">
      <h3>${i.title}</h3>
      <div class="meta">${i.source_group} • ${i.location} • ${i.salary || 'N/A'}</div>
      <p>${i.description || ''}</p>
      <div class="tags">${(i.tags || []).map(t => `<span class="tag">${t}</span>`).join('')}</div>
      <a href="${i.source_url}" target="_blank">Xem nguồn</a>
    </article>
  `).join('');
}

document.getElementById('searchBtn').addEventListener('click', fetchJobs);
fetchJobs();
