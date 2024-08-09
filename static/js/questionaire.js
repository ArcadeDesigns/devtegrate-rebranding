// JavaScript Logic
function SelectNextQuestion() {
    const nextBtn = document.querySelector('.nextBtn');
    const previousBtn = document.querySelector('.previousBtn');
    const questions = document.querySelectorAll('.questionaireCtnBoxCtn');
    let currentIndex = Array.from(questions).findIndex(q => q.classList.contains('active'));

    function updateQuestionVisibility() {
        questions.forEach((question, index) => {
            question.classList.toggle('active', index === currentIndex);
        });

        const indicator = document.querySelector('.indicator');
        if (indicator) {
            indicator.textContent = `${currentIndex + 1}/${questions.length} Questions`;
        }
    }

    function moveToQuestion(index) {
        currentIndex = index;
        updateQuestionVisibility();
    }

    nextBtn.addEventListener('click', () => {
        if (currentIndex < questions.length - 1) {
            currentIndex++;
            updateQuestionVisibility();
        }
    });

    previousBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateQuestionVisibility();
        }
    });

    updateQuestionVisibility();

    return moveToQuestion;
}

function PickOption() {
    const questionContainers = document.querySelectorAll('.questionaireCtnBoxCtn');
    const moveToQuestion = SelectNextQuestion();

    questionContainers.forEach(function(container, index) {
        const buttons = container.querySelectorAll('.smBtn');
        const hiddenInput = container.querySelector('.FlexBtnCtn > input[type="text"]');

        buttons.forEach(function(button) {
            button.addEventListener('click', function() {
                const answer = this.textContent.trim();
                if (hiddenInput) {
                    hiddenInput.value = answer;
                }

                if (index < questionContainers.length - 1) {
                    moveToQuestion(index + 1);
                }
            });
        });

        const checkboxes = container.querySelectorAll('.checkboxCtn input[type="checkbox"]');
        const readOnlyInput = container.querySelector('.ReadOnlyInput');

        checkboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', function() {
                const selectedOptions = Array.from(checkboxes)
                    .filter(cb => cb.checked)
                    .map(cb => cb.nextElementSibling.textContent.trim())
                    .join(', ');

                if (readOnlyInput) {
                    readOnlyInput.value = selectedOptions;
                }
            });
        });
    });
}

PickOption();

function SwitchQuestionnaireScreen() {
    const ActionSwitch = document.querySelector('.GetStarted');
    const ChangePageWithActionSwitch = document.querySelector('.questionaireSlide:not(.active)');

    ActionSwitch.addEventListener("click", function() {
        document.querySelector('.questionaireSlide.active').classList.remove('active');
        ChangePageWithActionSwitch.classList.add("active");
    });
}

function StartQuestionnaire() {
    const startBtn = document.querySelector('.StartQuestionaire');
    const moveToQuestion = SelectNextQuestion();

    startBtn.addEventListener('click', function() {
        moveToQuestion(1);
    });
}

SwitchQuestionnaireScreen();
StartQuestionnaire();