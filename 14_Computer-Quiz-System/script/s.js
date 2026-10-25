let name = '';
let id = '';
let questions = [];
let correctAnswers = 0;
let totalAnswers = 0;
function submitStudentInfo() {
    name = document.getElementById("student-name").value;
    id = document.getElementById("student-id").value;
    const idPattern = /^\d+$/;
    if (name && id && idPattern.test(id)) {
        studentInfoSubmitted = true;
        const infoContainer = document.getElementById("student-info-container");
        infoContainer.style.display = "none";
        const infoBox = document.createElement('div');
        infoBox.id = 'info-box';
        infoBox.innerHTML = ` ${name} |  ${id}`;
        document.body.appendChild(infoBox);
    }
}
function closePopup() {
    const popup = document.getElementById("popup");
    popup.style.display = "none";
}
function loadQuestionsFromFile() {
    fetch('json/q.json')
        .then(response => response.json())
        .then(data => {
            questions = data;
            totalAnswers = questions.length;
            loadQuestions();
        })
        .catch(error => {
            console.error('Error loading the questions file:', error);
        });
}
function loadQuestions() {
    const quizContainer = document.getElementById('quiz-container');
    quizContainer.innerHTML = '';
    questions.forEach((question, index) => {
        const questionContainer = document.createElement('div');
        questionContainer.classList.add('question-container');
        const questionElement = document.createElement('p');
        questionElement.classList.add('question');
        questionElement.innerText = question.question;
        const optionsList = document.createElement('ul');
        optionsList.classList.add('options');
        question.options.forEach(option => {
            const li = document.createElement('li');
            li.innerText = option;
            li.onclick = () => selectAnswer(li, question.correctAnswer, option);
            optionsList.appendChild(li);
        });
        questionContainer.appendChild(questionElement);
        questionContainer.appendChild(optionsList);
        quizContainer.appendChild(questionContainer);
    });
}
function selectAnswer(li, correctAnswer, selectedAnswer) {
    const allOptions = li.parentNode.querySelectorAll('li');
    allOptions.forEach(option => option.classList.remove('selected'));
    li.classList.add('selected');
    if (selectedAnswer === correctAnswer) {
        correctAnswers++;
    }
}
function showPopup(message) {
    const popup = document.getElementById('popup');
    const popupMessage = document.getElementById('popup-message');
    let wrongAnswers = totalAnswers - correctAnswers;
    let percentage = (correctAnswers / totalAnswers) * 100;
    popupMessage.innerHTML = `
        <strong> ${name} |  ${id}</strong><br>
        <strong>ตอบถูก: ${correctAnswers} ข้อ / ${totalAnswers} ข้อ</strong><br>
        ตอบผิด: ${wrongAnswers} ข้อ<br>
        คิดเป็น: ${percentage.toFixed(2)}%
        <br>เอาคะแนนที่ได้หารด้วย3<br>
        <br>คะแนนที่หารแล้ว:${correctAnswers / 3} <br>
    `;
    popup.style.display = 'block';
}
function submitQuiz() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
    showPopup("คำตอบถูกส่งแล้ว!");
}
loadQuestionsFromFile();
document.addEventListener('copy', function(e) {
    e.preventDefault();
    alert("การคัดลอกข้อความถูกปิดใช้งาน");
});
document.addEventListener('cut', function(e) {
    e.preventDefault();
    alert("การตัดข้อความถูกปิดใช้งาน");
});
