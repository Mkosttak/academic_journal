document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('form input[required], form textarea[required], form select[required]').forEach(function(el) {
        el.removeAttribute('required');
    });

    // Makale ekle formu için yazarlar alanı kontrolü
    const authorListDiv = document.getElementById('author-list');
    const hiddenAuthorsInput = document.getElementById('id_yazarlar_json');
    
    if (authorListDiv && hiddenAuthorsInput) {
        const addAuthorBtn = document.getElementById('add-author-btn');
        const authorInput = document.getElementById('author-input');
        const authorErrorDiv = document.getElementById('author-error-message');

        function addAuthorTag(isim_soyisim, username) {
            // Aynı yazar tekrar eklenmesin (isim ve username ile kontrol)
            const exists = Array.from(authorListDiv.children).some(tag => {
                return (tag.dataset.username && tag.dataset.username === (username || '')) ||
                       (!tag.dataset.username && !username && tag.dataset.isim_soyisim === isim_soyisim);
            });
            if (exists) return;
            const tag = document.createElement('div');
            tag.className = 'badge d-flex align-items-center p-2 text-dark-emphasis bg-light-subtle border border-dark-subtle rounded-pill';
            tag.dataset.isim_soyisim = isim_soyisim;
            tag.dataset.username = username || '';
            tag.innerHTML = `
                ${isim_soyisim} ${username ? '(@' + username + ')' : ''}
                ${username && username !== window.currentUsername ? '<button type="button" class="btn-close ms-2 remove-author-btn" aria-label="Close"></button>' : ''}
                ${!username ? '<button type="button" class="btn-close ms-2 remove-author-btn" aria-label="Close"></button>' : ''}
            `;
            authorListDiv.appendChild(tag);
            updateHiddenInput();
        }
        function updateHiddenInput() {
            const authorTags = authorListDiv.querySelectorAll('.badge');
            const authors = [];
            authorTags.forEach(tag => {
                authors.push({
                    isim_soyisim: tag.dataset.isim_soyisim,
                    username: tag.dataset.username || null
                });
            });
            hiddenAuthorsInput.value = JSON.stringify(authors);
        }
        function initializeAuthors() {
            let initialAuthors = [];
            try {
                if (hiddenAuthorsInput.value) {
                    initialAuthors = JSON.parse(hiddenAuthorsInput.value);
                }
            } catch (e) {
                console.error("Yazar verisi ayrıştırılamadı:", e);
                initialAuthors = [];
            }

            // Mevcut yazarları ekle
            initialAuthors.forEach(author => {
                addAuthorTag(author.isim_soyisim, author.username);
            });

            // Eğer hiç yazar yoksa ve currentUsername/currentFullName varsa, giriş yapan kullanıcıyı ekle
            if (!initialAuthors.length && window.currentUsername && window.currentFullName) {
                addAuthorTag(window.currentFullName, window.currentUsername);
            }
        }
        // Ekle tuşu event handler
        if (addAuthorBtn && authorInput) {
            addAuthorBtn.addEventListener('click', function() {
                const authorText = authorInput.value.trim();
                if (!authorText) {
                    authorErrorDiv.textContent = 'Yazar adı boş olamaz.';
                    return;
                }

                // CSRF token kontrolü
                const csrfToken = window.csrfToken || document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
                if (!csrfToken) {
                    console.error('CSRF token bulunamadı!');
                    authorErrorDiv.textContent = 'Güvenlik hatası oluştu. Sayfayı yenileyip tekrar deneyin.';
                    return;
                }

                // checkAuthorUrl kontrolü
                if (!window.checkAuthorUrl) {
                    console.error('checkAuthorUrl tanımlanmamış!');
                    authorErrorDiv.textContent = 'Sistem hatası oluştu. Sayfayı yenileyip tekrar deneyin.';
                    return;
                }

                const formData = new FormData();
                formData.append('author_text', authorText);
                formData.append('csrfmiddlewaretoken', csrfToken);

                authorErrorDiv.textContent = 'Yazar kontrol ediliyor...';
                fetch(window.checkAuthorUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw new Error(data.message || 'Sunucu hatası oluştu.');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'success') {
                        addAuthorTag(data.isim_soyisim, data.username);
                        authorInput.value = '';
                        authorErrorDiv.textContent = '';
                    } else {
                        authorErrorDiv.textContent = data.message || 'Bilinmeyen bir hata oluştu.';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    authorErrorDiv.textContent = error.message || 'Bir hata oluştu. Lütfen tekrar deneyin.';
                });
            });
        }
        // Silme işlemi
        authorListDiv.addEventListener('click', function(e) {
            if (e.target && e.target.classList.contains('remove-author-btn')) {
                // Kendi etiketi için kaldırma işlemini engelle
                const parentTag = e.target.parentElement;
                if (parentTag.dataset.username === window.currentUsername) {
                    return;
                }
                parentTag.remove();
                updateHiddenInput();
            }
        });
        initializeAuthors();
    }

    // Admin notu temizleme butonu
    const clearBtn = document.getElementById('clear-admin-note');
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            const noteInput = document.getElementById('id_admin_notu');
            if (noteInput) noteInput.value = '';
        });
    }

    // Profil resmi yönetimi
    const profilePicInput = document.getElementById('id_profile_resmi');
    const changePicButton = document.getElementById('change-pic-btn');
    const removePicButton = document.getElementById('remove-pic-btn');
    const imagePreview = document.getElementById('image-preview');
    const iconPlaceholder = document.getElementById('icon-placeholder');
    const filenameSpan = document.getElementById('pic-filename');
    
    if (changePicButton && profilePicInput) {
        changePicButton.addEventListener('click', function() {
            profilePicInput.click();
        });
    }

    if (profilePicInput) {
        profilePicInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (imagePreview && iconPlaceholder) {
                        imagePreview.src = e.target.result;
                        imagePreview.classList.remove('d-none');
                        iconPlaceholder.classList.add('d-none');
                    }
                };
                reader.readAsDataURL(file);

                if (filenameSpan) filenameSpan.textContent = file.name;
                if (removePicButton) removePicButton.classList.remove('d-none');
                
                const clearCheckbox = document.querySelector('input[name="profile_resmi-clear"]');
                if (clearCheckbox) clearCheckbox.checked = false;
            }
        });
    }

    if (removePicButton && imagePreview && iconPlaceholder) {
        removePicButton.addEventListener('click', function() {
            const clearCheckbox = document.querySelector('input[name="profile_resmi-clear"]');
            if (!clearCheckbox) {
                console.error('Temizle onay kutusu bulunamadı!');
                return;
            }

            clearCheckbox.checked = true;
            if (profilePicInput) profilePicInput.value = '';

            imagePreview.src = ''; 
            imagePreview.classList.add('d-none');
            iconPlaceholder.classList.remove('d-none');
            
            if (filenameSpan) filenameSpan.textContent = '';
            removePicButton.classList.add('d-none');
        });
    }

    // --- Inline JS from partials/_navbar.html ---
    let lastScrollTop = 0;
    const navbar = document.querySelector('.navbar-glass');
    const scrollThreshold = 50;
    if (navbar) {
        window.addEventListener('scroll', function() {
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            if (scrollTop > lastScrollTop && scrollTop > scrollThreshold) {
                navbar.classList.add('navbar-hidden');
                navbar.classList.remove('navbar-visible');
            } else {
                navbar.classList.remove('navbar-hidden');
                navbar.classList.add('navbar-visible');
            }
            lastScrollTop = scrollTop;
        });
    }

    // --- Inline JS from partials/_messages.html ---
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.forEach(function (toastEl) {
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toast = new bootstrap.Toast(toastEl, {
                animation: true,
                autohide: true,
                delay: 5000
            });
            toast.show();
        }
    });
});

/*
// Tıklanabilir profil resmi önizlemesi
const profilePicPreview = document.getElementById('profile-pic-preview');
if (profilePicPreview) {
    profilePicPreview.addEventListener('click', function() {
        profilePicInput.click();
    });
}
*/ 