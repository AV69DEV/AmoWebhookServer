// Простой скрипт для добавления плавной прокрутки
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

function handleErrorCallback(error, client_id) {
    console.log("Error during authorization:", error.error);

//Здесь будет отправка данных на сервер
    if (error.error === "access_denied") {
        alert("Вы отказались предоставить доступ. Пожалуйста, разрешите доступ для продолжения.");
    }
}

window.handleErrorCallback = handleErrorCallback;