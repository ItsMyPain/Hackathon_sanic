function myFunc(input) {
    const files = input.files || input.currentTarget.files;
    const reader = [];
    const images = document.getElementById('images');
    let name;
    for (const i in files) {
        if (files.hasOwnProperty(i)) {
            name = 'file' + i;

            reader[i] = new FileReader();
            reader[i].readAsDataURL(input.files[i]);

            images.innerHTML += '<img id="' + name + '" class="face_photo" src=""  alt=""/>';

            (function (name) {
                reader[i].onload = function (e) {
                    console.log(document.getElementById(name));
                    document.getElementById(name).src = e.target.result;
                };
            })(name);

            console.log(files[i]);
        }
    }
}