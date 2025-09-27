document.addEventListener('DOMContentLoaded', function() {
    const isEditorCheckbox = document.querySelector('#id_is_editor');
    const isChiefEditorField = document.querySelector('#id_is_chief_editor').closest('.form-row');
    const isChiefEditorCheckbox = document.querySelector('#id_is_chief_editor');
    const showOnEditorsPageCheckbox = document.querySelector('#id_goster_editorler_sayfasinda');
    
    function toggleChiefEditorField() {
        if (isEditorCheckbox && isChiefEditorField && showOnEditorsPageCheckbox) {
            // Baş editör seçeneği sadece hem editör yetkisi hem de editörler sayfasında görüntülenme seçenekleri işaretliyse görünür
            if (isEditorCheckbox.checked && showOnEditorsPageCheckbox.checked) {
                isChiefEditorField.style.display = 'block';
            } else {
                isChiefEditorField.style.display = 'none';
                if (isChiefEditorCheckbox) {
                    isChiefEditorCheckbox.checked = false;
                }
            }
        }
    }
    
    // Sayfa yüklendiğinde kontrol et
    toggleChiefEditorField();
    
    // Editör yetkisi değiştiğinde kontrol et
    if (isEditorCheckbox) {
        isEditorCheckbox.addEventListener('change', toggleChiefEditorField);
    }
    
    // Editörler sayfasında görüntülenme değiştiğinde kontrol et
    if (showOnEditorsPageCheckbox) {
        showOnEditorsPageCheckbox.addEventListener('change', toggleChiefEditorField);
    }
    
    // Baş editör değişikliğinde onay yok - direkt değişiklik
});
