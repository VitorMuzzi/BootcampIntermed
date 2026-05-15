function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'flex';
    setTimeout(() => {
        modal.classList.add('active');
    }, 10);
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('active');
    setTimeout(() => {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }, 300);
}

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        closeModal(event.target.id);
    }
}

function openTechModal(title, iconClass, text) {
    document.getElementById('modalTechTitle').innerText = title;
    document.getElementById('modalTechIcon').className = ''; 
    document.getElementById('modalTechIcon').classList.add('fa-brands');
    
    if (iconClass === 'fa-database') {
        document.getElementById('modalTechIcon').classList.replace('fa-brands', 'fa-solid');
    }
    document.getElementById('modalTechIcon').classList.add(iconClass);
    document.getElementById('modalTechText').innerText = text;
    
    openModal('techModal');
}

let currentProjectImages = [];

function openProjectModal(title, imagesArray, description, repoUrl, demoUrl) {
    document.getElementById('modalProjectTitle').innerText = title;
    document.getElementById('modalProjectDesc').innerText = description;
    
    const repoBtn = document.getElementById('modalProjectRepoBtn');
    if (repoUrl) {
        repoBtn.href = repoUrl;
        repoBtn.style.display = 'inline-flex';
    } else {
        repoBtn.style.display = 'none';
    }
    
    const demoBtn = document.getElementById('modalProjectDemoBtn');
    if (demoUrl) {
        demoBtn.href = demoUrl;
        demoBtn.style.display = 'inline-flex';
    } else {
        demoBtn.style.display = 'none';
    }

    currentProjectImages = imagesArray;
    const mainImg = document.getElementById('modalProjectMainImg');
    const thumbsContainer = document.getElementById('modalProjectThumbs');
    thumbsContainer.innerHTML = '';

    if (currentProjectImages.length > 0) {
        mainImg.src = currentProjectImages[0];
        mainImg.style.display = 'block';

        currentProjectImages.forEach((imgSrc, index) => {
            const thumb = document.createElement('img');
            thumb.src = imgSrc;
            thumb.alt = `Miniatura ${index + 1}`;
            thumb.classList.add('thumbnail');
            if (index === 0) thumb.classList.add('active');
            
            thumb.onclick = function() {
                changeMainImage(index);
            };
            thumbsContainer.appendChild(thumb);
        });
        thumbsContainer.style.display = 'flex';
    } else {
        mainImg.style.display = 'none';
        thumbsContainer.style.display = 'none';
    }

    openModal('projectModal');
}

function changeMainImage(index) {
    const mainImg = document.getElementById('modalProjectMainImg');
    mainImg.style.opacity = '0';
    
    setTimeout(() => {
        mainImg.src = currentProjectImages[index];
        mainImg.style.opacity = '1';
        
        const thumbs = document.querySelectorAll('.thumbnail');
        thumbs.forEach((t, i) => {
            if (i === index) t.classList.add('active');
            else t.classList.remove('active');
        });
    }, 200);
}

document.addEventListener('keydown', function(event) {
    const projectModal = document.getElementById('projectModal');
    if (projectModal.classList.contains('active') && currentProjectImages.length > 1) {
        let currentActiveIndex = currentProjectImages.indexOf(document.getElementById('modalProjectMainImg').src);
        
        if (event.key === 'ArrowRight') {
            let nextIndex = (currentActiveIndex + 1) % currentProjectImages.length;
            changeMainImage(nextIndex);
        } else if (event.key === 'ArrowLeft') {
            let prevIndex = (currentActiveIndex - 1 + currentProjectImages.length) % currentProjectImages.length;
            changeMainImage(prevIndex);
        }
    }
});