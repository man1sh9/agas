let galleryTexts = {};

function toggleMenu() {
    const navLinks = document.getElementById('nav-links');
    if (navLinks) navLinks.classList.toggle('active');
}

function openLightbox(src) {
    const lightbox = document.getElementById('lightbox');
    const img = document.getElementById('lightboxImage');
    if (!lightbox || !img) return;
    img.src = src;
    lightbox.style.display = 'flex';
}

function closeLightbox(event) {
    const target = event.target;
    if (target.id === 'lightbox' || (target.classList && target.classList.contains('close'))) {
        const lightbox = document.getElementById('lightbox');
        const img = document.getElementById('lightboxImage');
        if (lightbox) lightbox.style.display = 'none';
        if (img) img.src = '';
    }
}

function showCaption(index, lang) {
    const box = document.getElementById(`caption-${index}`);
    if (!box) return;
    const text = (galleryTexts[index] && galleryTexts[index][lang]) || '';
    box.innerText = text;
    box.style.display = 'block';
}

function loadGalleryTexts() {
    const dataNode = document.getElementById('gallery-texts');
    if (!dataNode) return;
    try {
        galleryTexts = JSON.parse(dataNode.textContent);
    } catch (err) {
        console.error('Failed to parse gallery texts', err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadGalleryTexts();
    document.querySelectorAll('.caption-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            const index = parseInt(btn.getAttribute('data-caption-index'), 10);
            const lang = btn.getAttribute('data-caption-lang');
            showCaption(index, lang);
        });
    });
});
