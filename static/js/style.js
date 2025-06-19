// Tüm formlardaki required attribute'unu kaldır
// Böylece sadece Django'nun sunucu tarafı validasyonu ve özel hata kutuları çalışır

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('form input[required], form textarea[required], form select[required]').forEach(function(el) {
        el.removeAttribute('required');
    });

    // Makale ekle formu için yazarlar alanı kontrolü
    if (document.getElementById('author-list') && window.currentUsername && window.currentFullName && window.checkAuthorUrl) {
        const addAuthorBtn = document.getElementById('add-author-btn');
        const authorInput = document.getElementById('author-input');
        const authorListDiv = document.getElementById('author-list');
        const authorErrorDiv = document.getElementById('author-error-message');
        const hiddenAuthorsInput = document.getElementById('id_yazarlar_json');

        function addAuthorTag(isim_soyisim, username) {
            // Aynı yazar tekrar eklenmesin
            const exists = Array.from(authorListDiv.children).some(tag => tag.dataset.username === username && username);
            if (exists) return;
            const tag = document.createElement('div');
            tag.className = 'badge d-flex align-items-center p-2 text-dark-emphasis bg-light-subtle border border-dark-subtle rounded-pill';
            tag.dataset.isim_soyisim = isim_soyisim;
            tag.dataset.username = username || '';
            tag.innerHTML = `
                ${isim_soyisim} ${username ? '(@' + username + ')' : ''}
                ${username && username !== window.currentUsername ? '<button type="button" class="btn-close ms-2 remove-author-btn" aria-label="Close"></button>' : ''}
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
                initialAuthors = [];
            }
            // Eğer hiç yazar yoksa, giriş yapan kullanıcıyı ekle
            if (!initialAuthors.length) {
                initialAuthors = [{isim_soyisim: window.currentFullName, username: window.currentUsername}];
            }
            // Giriş yapan kullanıcı mutlaka ilk sırada ve silinemez olsun
            let foundSelf = false;
            initialAuthors.forEach(author => {
                if (author.username === window.currentUsername) {
                    foundSelf = true;
                    addAuthorTag(author.isim_soyisim, author.username);
                }
            });
            if (!foundSelf) {
                addAuthorTag(window.currentFullName, window.currentUsername);
            }
            // Diğer yazarları ekle
            initialAuthors.forEach(author => {
                if (author.username !== window.currentUsername) {
                    addAuthorTag(author.isim_soyisim, author.username);
                }
            });
        }
        // Ekle tuşu event handler
        if (addAuthorBtn && authorInput) {
            addAuthorBtn.addEventListener('click', function() {
                const authorText = authorInput.value.trim();
                if (!authorText) return;
                const formData = new FormData();
                formData.append('author_text', authorText);
                // CSRF token'ı formdan al
                const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
                formData.append('csrfmiddlewaretoken', csrfInput ? csrfInput.value : '');
                fetch(window.checkAuthorUrl, {
                    method: 'POST',
                    body: formData,
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        addAuthorTag(data.isim_soyisim, data.username);
                        authorInput.value = '';
                        authorErrorDiv.textContent = '';
                    } else {
                        authorErrorDiv.textContent = data.message;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    authorErrorDiv.textContent = 'Bir hata oluştu. Lütfen tekrar deneyin.';
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
}); 