// HealthApp - Основной объект приложения
const HealthApp = {
  // Состояние приложения
  currentUser: null,
  currentScreen: 'loadingScreen',
  currentSymptom: null,
  healthData: [],
  events: [],
  isGosLinked: false,
  savedClinics: [],
  connectedDevices: [],
  _chart: null,

  // Инициализация приложения
  init() {
    console.log('Инициализация приложения...');
    this.loadFromStorage();
    this.setupEventListeners();

    // Ждем полной загрузки DOM
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        this.checkProfileAndNavigate();
      });
    } else {
      setTimeout(() => this.checkProfileAndNavigate(), 100);
    }
  },

  // Загрузка данных из localStorage
  loadFromStorage() {
    try {
      const savedUser = localStorage.getItem('healthCompassUser');
      if (savedUser) this.currentUser = JSON.parse(savedUser);

      this.healthData = JSON.parse(localStorage.getItem('healthData') || '[]');
      this.events = JSON.parse(localStorage.getItem('hcEvents') || '[]');
      this.isGosLinked = JSON.parse(localStorage.getItem('gosLinked') || 'false');
      this.savedClinics = JSON.parse(localStorage.getItem('savedClinics') || '[]');
      this.connectedDevices = JSON.parse(localStorage.getItem('connectedDevices') || '[]');

      console.log('Данные загружены:', {
        user: !!this.currentUser,
        healthData: this.healthData.length,
        events: this.events.length
      });
    } catch (e) {
      console.error('Ошибка загрузки данных:', e);
      // Сбрасываем поврежденные данные
      this.healthData = [];
      this.events = [];
      this.savedClinics = [];
      this.connectedDevices = [];
    }
  },

  // Проверка заполненности профиля
  isProfileComplete(u) {
    if (!u) return false;
    const required = ['fullName', 'birthYear', 'gender', 'bloodType', 'weight', 'height', 'emergencyContact'];
    return required.every(field => u[field] && u[field].toString().trim() !== '');
  },

  // Сохранение профиля
  saveProfile() {
    try {
      const bloodType = document.getElementById('bloodType').value;
      const rhFactor = document.getElementById('rhFactor').value;

      if (!bloodType || !rhFactor) {
        this.showNotification('Заполните группу крови и резус-фактор');
        return;
      }

      const finalBT = bloodType + rhFactor;
      const birthYear = parseInt(document.getElementById('birthYear').value);
      const currentYear = new Date().getFullYear();
      const age = currentYear - birthYear;

      this.currentUser = {
        fullName: document.getElementById('fullName').value.trim(),
        birthYear: birthYear,
        age: age,
        gender: document.getElementById('gender').value,
        bloodType: finalBT,
        weight: parseFloat(document.getElementById('weight').value),
        height: parseInt(document.getElementById('height').value),
        emergencyContact: document.getElementById('emergencyContact').value.trim(),
        healthConditions: {
          allergies: document.getElementById('allergies').value.trim(),
          vision: document.getElementById('vision').value,
          workType: document.getElementById('workType').value,
          medicalHistory: document.getElementById('medicalHistory').value.trim(),
          currentConditions: document.getElementById('currentConditions').value.trim()
        }
      };

      localStorage.setItem('healthCompassUser', JSON.stringify(this.currentUser));
      this.showNotification('Профиль сохранён');
      this.updateUIWithUserData();
      this.buildPlanAndCalendar();
      this.generateHealthRecommendations();
      this.showScreen('mainScreen');
    } catch (e) {
      console.error('Ошибка сохранения:', e);
      this.showNotification('Ошибка при сохранении профиля');
    }
  },

  // Обновление UI данными пользователя
  updateUIWithUserData() {
    if (!this.currentUser) return;

    const userNameEl = document.getElementById('userName');
    if (userNameEl) {
      // Извлекаем имя (второе слово в ФИО)
      const nameParts = this.currentUser.fullName.split(' ');
      const firstName = nameParts.length > 1 ? nameParts[1] : nameParts[0];
      userNameEl.textContent = firstName || 'Пользователь';
    }

    const userAvatar = document.getElementById('userAvatar');
    if (userAvatar) {
      userAvatar.textContent = this.currentUser.fullName.charAt(0).toUpperCase() || 'U';
    }

    // Обновляем статус Госуслуг
    const gosStatus = document.getElementById('gosStatus');
    const linkBtn = document.getElementById('linkGosuslugiBtn');
    const unlinkBtn = document.getElementById('unlinkGosuslugiBtn');

    if (gosStatus && linkBtn && unlinkBtn) {
      gosStatus.textContent = this.isGosLinked ? 'Статус: привязан' : 'Статус: не привязан';
      linkBtn.style.display = this.isGosLinked ? 'none' : 'inline-flex';
      unlinkBtn.style.display = this.isGosLinked ? 'inline-flex' : 'none';
    }
  },

  // Настройка обработчиков событий
  setupEventListeners() {
    console.log('Настройка обработчиков...');

    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
      profileForm.addEventListener('submit', e => {
        e.preventDefault();
        this.saveProfile();
      });
    }

    // Кнопки Госуслуг
    const linkBtn = document.getElementById('linkGosuslugiBtn');
    const unlinkBtn = document.getElementById('unlinkGosuslugiBtn');

    if (linkBtn) linkBtn.addEventListener('click', () => this.linkGosuslugi());
    if (unlinkBtn) unlinkBtn.addEventListener('click', () => this.unlinkGosuslugi());

    // Глобальные функции
    window.showScreen = (id) => this.showScreen(id);
    window.selectSymptomArea = (key, name) => this.selectSymptomArea(key, name);
    window.callClinic = (phone) => this.callClinic(phone);
    window.showClinicOnMap = () => this.showClinicOnMap();
    window.saveHealthData = () => this.saveHealthData();
    window.clearDiary = () => this.clearDiary();
    window.exportICS = () => this.exportICS();
    window.logout = () => this.logout();
    window.renderChart = (type) => this.renderChart(type);
    window.addCustomEvent = () => this.addCustomEvent();
    window.findNearbyClinics = () => this.findNearbyClinics();
    window.saveClinic = (id) => this.saveClinic(id);
    window.bookOnline = (id) => this.bookOnline(id);
    window.connectDevice = () => this.connectDevice();
    window.toggleSwitch = (el) => this.toggleSwitch(el);
    window.showEventDetail = (id) => this.showEventDetail(id);
    window.toggleEventDetail = (id) => this.toggleEventDetail(id);
    window.resetSymptomSelection = () => this.resetSymptomSelection();

    console.log('Обработчики настроены');
  },

  // Переключение экранов
  showScreen(id) {
    console.log('Переход на экран:', id);

    // Скрываем все экраны
    document.querySelectorAll('.screen').forEach(s => {
      s.classList.remove('active');
    });

    // Показываем целевой экран
    const target = document.getElementById(id);
    if (target) {
      target.classList.add('active');
      this.currentScreen = id;
      this.initializeScreen(id);
    } else {
      console.error('Экран не найден:', id);
      this.showScreen('mainScreen'); // fallback
    }

    // Обновляем навигацию
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(n => n.classList.remove('active'));

    const navMap = {
      'mainScreen': 0,
      'preventionScreen': 1,
      'wellnessScreen': 2,
      'diaryScreen': 3,
      'communityScreen': 4
    };

    if (navMap[id] !== undefined && navItems[navMap[id]]) {
      navItems[navMap[id]].classList.add('active');
    }
  },

  // Инициализация экрана
  initializeScreen(id) {
    console.log('Инициализация экрана:', id);

    switch(id) {
      case 'diaryScreen':
        this.renderChart('weight');
        this.updateDailyRecommendations();
        break;
      case 'mainScreen':
        this.refreshMainStats();
        break;
      case 'preventionScreen':
        this.renderCalendarList();
        this.renderMandatoryExaminations();
        this.renderDispanserizationInfo();
        break;
      case 'clinicsScreen':
        this.renderSavedClinics();
        break;
      case 'wellnessScreen':
        this.calculateWellnessScore();
        break;
      case 'symptomsScreen':
        this.resetSymptomSelection();
        break;
    }
  },

  // Проверка профиля и навигация
  checkProfileAndNavigate() {
    console.log('Проверка профиля...', this.currentUser);

    if (this.currentUser && this.isProfileComplete(this.currentUser)) {
      console.log('Профиль заполнен, переход на главную');
      this.updateUIWithUserData();
      this.buildPlanAndCalendar();
      this.generateHealthRecommendations();
      this.showScreen('mainScreen');
    } else {
      console.log('Профиль не заполнен, переход к созданию профиля');
      this.showScreen('profileScreen');
    }

    // Скрываем экран загрузки
    const loadingScreen = document.getElementById('loadingScreen');
    if (loadingScreen) {
      loadingScreen.classList.remove('active');
    }
  },

  // Показать детали события
  showEventDetail(eventId) {
    const event = this.events.find(e => e.id === eventId);
    if (event) {
      this.showModal(event.title, event.detailedDescription || event.desc || 'Описание отсутствует');
    }
  },

  // Переключить отображение деталей события
  toggleEventDetail(eventId) {
    const detailElement = document.getElementById(`event-detail-${eventId}`);
    if (detailElement) {
      detailElement.classList.toggle('active');
    }
  },

  // Модальное окно
  showModal(title, content) {
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '10000';

    const modalContent = document.createElement('div');
    modalContent.style.background = 'white';
    modalContent.style.padding = '20px';
    modalContent.style.borderRadius = '8px';
    modalContent.style.maxWidth = '80%';
    modalContent.style.maxHeight = '80%';
    modalContent.style.overflow = 'auto';

    modalContent.innerHTML = `
      <h2>${title}</h2>
      <div style="max-height: 400px; overflow-y: auto; margin: 15px 0;">
        ${content}
      </div>
      <button class="btn btn-primary" onclick="this.parentElement.parentElement.remove()" style="width: auto;">Закрыть</button>
    `;

    modal.appendChild(modalContent);
    document.body.appendChild(modal);
  },

  // Генерация рекомендаций по здоровью
  generateHealthRecommendations() {
    if (!this.currentUser) return;

    const conditions = this.currentUser.healthConditions || {};
    const recommendations = {
      examinations: this.generateExaminationRecommendations(conditions),
      exercises: this.generateExerciseRecommendations(conditions),
      nutrition: this.generateNutritionRecommendations(conditions)
    };

    this.displayRecommendations(recommendations);
  },

  // Рекомендации по обследованиям
  generateExaminationRecommendations(conditions) {
    const exams = [];

    exams.push('💉 Общий анализ крови - ежегодно');
    exams.push('🦷 Стоматолог - каждые 6 месяцев');
    exams.push('👁 Офтальмолог - ежегодно');
    exams.push('❤️ Кардиолог - раз в 2 года (ЭКГ)');

    if (this.currentUser.gender === 'female') {
      exams.push('👩 Гинеколог - ежегодно');
      if (this.currentUser.age >= 40) exams.push('👙 Маммолог - ежегодно');
    } else {
      if (this.currentUser.age >= 45) exams.push('👨 Уролог - ежегодно');
    }

    if (conditions.allergies) exams.push('🤧 Аллерголог - по показаниям');
    if (conditions.vision && conditions.vision !== 'normal') exams.push('👓 Офтальмолог - каждые 6 месяцев');
    if (conditions.workType === 'sedentary') exams.push('🦴 Ортопед - раз в 2 года');

    return exams;
  },

  // Рекомендации по упражнениям
  generateExerciseRecommendations(conditions) {
    const exercises = [];

    exercises.push('🚶 Ежедневная ходьба 30-60 минут');

    if (conditions.workType === 'sedentary') {
      exercises.push('💺 Упражнения для спины каждые 2 часа');
      exercises.push('👀 Гимнастика для глаз каждый час');
    } else if (conditions.workType === 'standing') {
      exercises.push('🦵 Упражнения для ног и вен');
      exercises.push('🧘 Растяжка спины ежедневно');
    }

    if (conditions.vision === 'myopia') exercises.push('👁 Гимнастика для глаз по Жданову');
    if (conditions.currentConditions && conditions.currentConditions.includes('гипертония')) {
      exercises.push('🏊 Плавание 2-3 раза в неделю');
    }

    return exercises;
  },

  // Рекомендации по питанию
  generateNutritionRecommendations(conditions) {
    const nutrition = [];
    const bloodType = this.currentUser.bloodType;

    const bloodTypeNutrition = {
      '0': ['🍖 Белковая диета', '💊 Витамины B, K'],
      'A': ['🥗 Вегетарианское питание', '💊 Витамины C, E'],
      'B': ['🥛 Сбалансированная диета', '💊 Магний'],
      'AB': ['🍣 Смешанное питание', '💊 Цинк, селен']
    };

    if (bloodTypeNutrition[bloodType]) {
      nutrition.push(...bloodTypeNutrition[bloodType]);
    }

    if (conditions.allergies) nutrition.push('🚫 Исключить аллергены из рациона');
    if (conditions.currentConditions && conditions.currentConditions.includes('диабет')) {
      nutrition.push('📊 Контроль углеводов');
      nutrition.push('🕒 Дробное питание 5-6 раз в день');
    }

    nutrition.push('💧 2 литра воды в день');
    nutrition.push('🥦 5 порций овощей и фруктов ежедневно');

    return nutrition;
  },

  // Отображение рекомендаций
  displayRecommendations(recommendations) {
    const examEl = document.getElementById('examinationRecommendations');
    const exerciseEl = document.getElementById('exerciseRecommendations');
    const nutritionEl = document.getElementById('nutritionRecommendations');

    if (examEl) examEl.innerHTML = recommendations.examinations.map(e => `<p>• ${e}</p>`).join('');
    if (exerciseEl) exerciseEl.innerHTML = recommendations.exercises.map(e => `<p>• ${e}</p>`).join('');
    if (nutritionEl) nutritionEl.innerHTML = recommendations.nutrition.map(n => `<p>• ${n}</p>`).join('');
  },

  // Обязательные обследования
  renderMandatoryExaminations() {
    const exams = [
      '🦷 Стоматолог - 2 раза в год',
      '👁 Офтальмолог - 1 раз в год',
      '👨‍⚕️ Терапевт - общее обследование 1 раз в год',
      '❤️ Кардиолог - ЭКГ 1 раз в 2 года'
    ];

    if (this.currentUser) {
      if (this.currentUser.gender === 'female') {
        exams.push('👩 Гинеколог - 1 раз в год');
        if (this.currentUser.age >= 40) exams.push('👙 Маммолог - 1 раз в год');
      } else {
        if (this.currentUser.age >= 45) exams.push('👨 Уролог - 1 раз в год');
      }
    }

    const container = document.getElementById('mandatoryExaminations');
    if (container) {
      container.innerHTML = exams.map(e => `<p>• ${e}</p>`).join('');
    }
  },

  // Информация о диспансеризации
  renderDispanserizationInfo() {
    if (!this.currentUser) return;

    const currentYear = new Date().getFullYear();
    const age = this.currentUser.age;
    const birthYear = this.currentUser.birthYear;

    // Определяем, положена ли диспансеризация в текущем году
    const dispanserizationYears = [1987, 1990, 1993, 1996, 1999, 2002, 2005, 2008];
    const isDispanserizationYear = dispanserizationYears.includes(birthYear) || age >= 40;

    let html = '';

    if (isDispanserizationYear) {
      html = `
        <div class="recommendation-card">
          <strong>📅 Вам положена диспансеризация в ${currentYear} году!</strong>
          <p>Запишитесь через портал «Госуслуги» или в поликлинике по месту прикрепления.</p>
          <button class="btn btn-primary" onclick="HealthApp.bookDispanserization()" style="margin-top: 8px;">
            <i class="fas fa-calendar-check"></i> Записаться на диспансеризацию
          </button>
        </div>
      `;
    } else {
      html = `
        <p>В ${currentYear} году диспансеризация не положена. Следующая диспансеризация по графику:</p>
        <p><strong>Годы рождения для диспансеризации:</strong> 1987, 1990, 1993, 1996, 1999, 2002, 2005, 2008</p>
      `;
    }

    html += `
      <div style="margin-top: 16px;">
        <h4>Что такое диспансеризация?</h4>
        <p>Диспансеризация — это бесплатное комплексное обследование, которое помогает выявить заболевания на ранней стадии.</p>
        
        <h4>Что входит в диспансеризацию?</h4>
        <ul>
          <li>Анкетирование и опрос о жалобах</li>
          <li>Измерение давления, роста, веса, расчет ИМТ</li>
          <li>Анализы крови (общий, холестерин, глюкоза)</li>
          <li>Флюорография и ЭКГ</li>
          <li>Осмотр терапевта</li>
          ${age >= 40 ? '<li>Измерение внутриглазного давления</li>' : ''}
          ${age >= 40 && age <= 64 ? '<li>Анализ кала на скрытую кровь (2 раза)</li>' : ''}
          ${age >= 45 ? '<li>Гастроскопия (однократно)</li>' : ''}
          ${this.currentUser.gender === 'female' && age >= 40 && age <= 75 ? '<li>Маммография (раз в 2 года)</li>' : ''}
          ${this.currentUser.gender === 'male' && [45, 50, 55, 60, 64].includes(age) ? '<li>Анализ ПСА для мужчин</li>' : ''}
        </ul>
        
        <p><strong>Что взять с собой:</strong> паспорт и полис ОМС</p>
        <p><strong>Время прохождения:</strong> обычно 1 рабочий день</p>
      </div>
    `;

    const container = document.getElementById('dispanserizationInfo');
    if (container) {
      container.innerHTML = html;
    }
  },

  // Запись на диспансеризацию
  bookDispanserization() {
    this.showNotification('Открывается портал Госуслуги для записи на диспансеризацию...');
    setTimeout(() => {
      window.open('https://www.gosuslugi.ru/health', '_blank');
    }, 1000);
  },

  // Сохранение данных здоровья
  saveHealthData() {
    const entry = {
      date: new Date(),
      syst: parseFloat(document.getElementById('bpSyst').value || ''),
      diast: parseFloat(document.getElementById('bpDiast').value || ''),
      pulse: parseFloat(document.getElementById('pulse').value || ''),
      weight: parseFloat(document.getElementById('diaryWeight').value || ''),
      glucose: parseFloat(document.getElementById('glucose').value || ''),
      steps: parseInt(document.getElementById('steps').value || ''),
      sleep: parseFloat(document.getElementById('sleep').value || ''),
      note: document.getElementById('note').value || ''
    };

    if (Object.values(entry).every(v => !v || v === 0)) {
      this.showNotification('Заполните хотя бы одно поле');
      return;
    }

    this.healthData.push(entry);
    localStorage.setItem('healthData', JSON.stringify(this.healthData));
    this.showNotification('Данные сохранены');

    ['bpSyst', 'bpDiast', 'pulse', 'diaryWeight', 'glucose', 'steps', 'sleep', 'note'].forEach(id => {
      document.getElementById(id).value = '';
    });

    this.refreshMainStats();
    if (this.currentScreen === 'diaryScreen') this.renderChart('weight');
    this.updateDailyRecommendations();
  },

  // Обновление ежедневных рекомендаций
  updateDailyRecommendations() {
    const lastEntry = this.healthData[this.healthData.length - 1];
    if (!lastEntry) {
      document.getElementById('dailyRecommendations').innerHTML = `
        <div class="recommendation-card">
          <strong>💪 Начните вести дневник здоровья</strong>
          <p>Заполните данные для получения персональных рекомендаций</p>
        </div>
      `;
      return;
    }

    let recommendations = [];

    // Расчет ИМТ и рекомендации по весу
    if (lastEntry.weight && this.currentUser.height) {
      const bmi = lastEntry.weight / ((this.currentUser.height / 100) ** 2);
      if (bmi < 18.5) {
        recommendations.push('📉 Ваш вес ниже нормы. Рекомендуется проконсультироваться с врачом.');
      } else if (bmi >= 18.5 && bmi <= 24.9) {
        recommendations.push('✅ Ваш вес в норме. Продолжайте поддерживать здоровый образ жизни!');
      } else if (bmi >= 25 && bmi <= 29.9) {
        recommendations.push('⚠️ У вас избыточный вес. Рекомендуется увеличить физическую активность.');
      } else {
        recommendations.push('🚨 У вас ожирение. Рекомендуется обратиться к врачу для консультации.');
      }
    }

    // Рекомендации по давлению
    if (lastEntry.syst && lastEntry.diast) {
      if (lastEntry.syst < 90 || lastEntry.diast < 60) {
        recommendations.push('🩸 Пониженное давление. Рекомендуется проконсультироваться с врачом.');
      } else if (lastEntry.syst > 140 || lastEntry.diast > 90) {
        recommendations.push('❤️ Повышенное давление. Рекомендуется проконсультироваться с кардиологом.');
      } else {
        recommendations.push('✅ Артериальное давление в норме.');
      }
    }

    // Рекомендации по пульсу
    if (lastEntry.pulse) {
      if (lastEntry.pulse < 60) {
        recommendations.push('🫀 Низкий пульс. Рекомендуется проконсультироваться с врачом.');
      } else if (lastEntry.pulse > 100) {
        recommendations.push('💓 Высокий пульс. Рекомендуется проконсультироваться с кардиологом.');
      } else {
        recommendations.push('✅ Пульс в норме.');
      }
    }

    // Рекомендации по глюкозе
    if (lastEntry.glucose) {
      if (lastEntry.glucose < 3.9) {
        recommendations.push('🩸 Низкий уровень глюкозы. Рекомендуется проконсультироваться с врачом.');
      } else if (lastEntry.glucose > 5.5) {
        recommendations.push('🍬 Повышенный уровень глюкозы. Рекомендуется проконсультироваться с эндокринологом.');
      } else {
        recommendations.push('✅ Уровень глюкозы в норме.');
      }
    }

    // Рекомендации по сну
    if (lastEntry.sleep) {
      if (lastEntry.sleep < 6) {
        recommendations.push('😴 Недостаточно сна. Рекомендуется спать 7-9 часов в сутки.');
      } else if (lastEntry.sleep > 9) {
        recommendations.push('🛌 Избыток сна. Рекомендуется 7-9 часов в сутки.');
      } else {
        recommendations.push('💤 Продолжительность сна в норме.');
      }
    }

    // Рекомендации по шагам
    if (lastEntry.steps) {
      if (lastEntry.steps < 5000) {
        recommendations.push('🚶‍♂️ Низкая активность. Рекомендуется увеличить количество шагов до 10,000 в день.');
      } else if (lastEntry.steps >= 5000 && lastEntry.steps < 10000) {
        recommendations.push('🏃‍♂️ Средняя активность. Отлично! Стремитесь к 10,000 шагов в день.');
      } else {
        recommendations.push('🎯 Отличная активность! Продолжайте в том же духе.');
      }
    }

    const container = document.getElementById('dailyRecommendations');
    if (container) {
      if (recommendations.length > 0) {
        container.innerHTML = recommendations.map(rec =>
          `<div class="recommendation-card"><p>${rec}</p></div>`
        ).join('');
      } else {
        container.innerHTML = `
          <div class="recommendation-card">
            <strong>📊 Заполните данные для получения рекомендаций</strong>
            <p>Введите показатели здоровья для персонализированных советов</p>
          </div>
        `;
      }
    }
  },

  // Подключение умных устройств
  connectDevice() {
    this.showNotification('Поиск устройств...');
    setTimeout(() => {
      const devices = ['Apple Watch', 'Глюкометр Accu-Chek', 'Тонометр Omron'];
      const randomDevice = devices[Math.floor(Math.random() * devices.length)];
      this.connectedDevices.push(randomDevice);
      localStorage.setItem('connectedDevices', JSON.stringify(this.connectedDevices));
      this.showNotification(`${randomDevice} подключен!`);
    }, 2000);
  },

  // Поиск клиник по геолокации
  findNearbyClinics() {
    if (!navigator.geolocation) {
      this.showNotification('Геолокация не поддерживается');
      return;
    }

    document.getElementById('locationStatus').textContent = 'Определение местоположения...';

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        document.getElementById('locationStatus').textContent = `Найдено 5 клиник в радиусе 2 км`;
        this.showNotification('Ближайшие клиники найдены!');
      },
      (error) => {
        document.getElementById('locationStatus').textContent = 'Не удалось определить местоположение';
        this.showNotification('Разрешите доступ к геолокации');
      }
    );
  },

  // Сохранение клиники
  saveClinic(clinicId) {
    const clinics = {
      'polyclinic1': { name: 'Городская поликлиника №1', address: 'ул. Ленина, 15' },
      'health-center': { name: 'Медцентр «Здоровье»', address: 'пр. Мира, 42' }
    };

    const clinic = clinics[clinicId];
    if (clinic && !this.savedClinics.find(c => c.id === clinicId)) {
      this.savedClinics.push({ id: clinicId, ...clinic });
      localStorage.setItem('savedClinics', JSON.stringify(this.savedClinics));
      this.showNotification('Клиника сохранена!');
      this.renderSavedClinics();
    }
  },

  // Отображение сохраненных клиник
  renderSavedClinics() {
    const container = document.getElementById('savedClinicsList');
    const card = document.getElementById('savedClinicsCard');

    if (this.savedClinics.length === 0) {
      card.style.display = 'none';
      return;
    }

    card.style.display = 'block';
    container.innerHTML = this.savedClinics.map(clinic => `
      <div class="clinic-card">
        <div class="clinic-name">${clinic.name}</div>
        <div class="muted">${clinic.address}</div>
        <div class="inline" style="margin-top:12px">
          <button class="btn btn-secondary" onclick="bookOnline('${clinic.id}')">
            <i class="fas fa-calendar-check"></i> Запись онлайн
          </button>
          <button class="btn" onclick="HealthApp.removeClinic('${clinic.id}')">
            <i class="fas fa-trash"></i> Удалить
          </button>
        </div>
      </div>
    `).join('');
  },

  // Удаление клиники
  removeClinic(clinicId) {
    this.savedClinics = this.savedClinics.filter(c => c.id !== clinicId);
    localStorage.setItem('savedClinics', JSON.stringify(this.savedClinics));
    this.renderSavedClinics();
    this.showNotification('Клиника удалена');
  },

  // Онлайн-запись в клинику
  bookOnline(clinicId) {
    this.showNotification('Переход на сайт записи...');
    setTimeout(() => {
      window.open('https://example-booking.com', '_blank');
    }, 1000);
  },

  // Расчет общей оценки здоровья
  calculateWellnessScore() {
    const { score, label, color } = this.computeWellness();
    document.getElementById('overallScore').textContent = `${100 - Math.round(score)}%`;
    document.getElementById('riskLevel').textContent = label;
    document.getElementById('riskLevel').style.color = color;

    // Обновляем прогресс-бары
    document.getElementById('physicalProgress').style.width = `${100 - score}%`;
    document.getElementById('lifestyleProgress').style.width = `${Math.max(60, 100 - score - 10)}%`;
    document.getElementById('preventionProgress').style.width = `${Math.min(100, 100 - score + 15)}%`;
  },

  // Построение плана обследований и календаря
  buildPlanAndCalendar() {
    if (!this.currentUser) return;
    const age = this.currentUser.age, gender = this.currentUser.gender;
    const plan = [];
    const push = (title, freq, note, condition = true, detailedDescription = '') => {
      if (condition) plan.push({ title, freq, note, detailedDescription })
    };

    // Базовые обследования для всех возрастов
    push('Общий анализ крови', 'ежегодно', 'Выявление анемии и воспалений', true,
      '<strong>Общий анализ крови (ОАК)</strong> позволяет:<br><br>' +
      '<strong>Оценить общее состояние организма:</strong> По результатам анализа врач может определить наличие воспалений, инфекции или других отклонений.<br><br>' +
      '<strong>Диагностировать заболевания крови:</strong> ОАК помогает выявить анемию, лейкоз, нарушения свертываемости крови.<br><br>' +
      '<strong>Контролировать лечение:</strong> При наличии хронических заболеваний ОАК помогает следить за динамикой и корректировать терапию.<br><br>' +
      '<strong>ОАК позволяет проверить:</strong><br>' +
      '<ul>' +
      '<li>Количество эритроцитов и уровень гемоглобина (для диагностики анемии)</li>' +
      '<li>Количество лейкоцитов и лейкоцитарную формулу (для выявления воспалений и инфекций)</li>' +
      '<li>Количество тромбоцитов (для оценки свертываемости крови)</li>' +
      '<li>Скорость оседания эритроцитов (СОЭ) - неспецифический показатель воспаления</li>' +
      '</ul><br>' +
      '<strong>При каких симптомах следует пройти обследование:</strong><br>' +
      '<ul>' +
      '<li>Повышенная утомляемость, слабость</li>' +
      '<li>Бледность кожи и слизистых</li>' +
      '<li>Частые инфекционные заболевания</li>' +
      '<li>Необъяснимые кровоподтеки или кровотечения</li>' +
      '<li>Потеря веса без видимой причины</li>' +
      '</ul>');

    push('Общий анализ мочи', 'ежегодно', 'Проверка почек и обмена веществ', true,
      '<strong>Общий анализ мочи (ОАМ)</strong> позволяет:<br><br>' +
      '<strong>Оценить общее состояние организма:</strong> По результатам анализа врач может определить наличие воспалений, инфекции или других отклонений.<br><br>' +
      '<strong>Диагностировать заболевания почек и мочевыводящих путей:</strong> ОАМ помогает выявить ранние признаки заболеваний, таких как пиелонефрит, цистит или гломерулонефрит.<br><br>' +
      '<strong>Контролировать лечение:</strong> При наличии хронических заболеваний почек ОАМ помогает следить за динамикой и корректировать терапию.<br><br>' +
      '<strong>ОАМ позволяет проверить:</strong><br>' +
      '<ul>' +
      '<li>Физические свойства мочи: цвет, прозрачность, удельный вес (плотность)</li>' +
      '<li>Химический состав: кислотность (pH), наличие белка, глюкозы, кетоновых тел, билирубина, уробилиногена, нитритов</li>' +
      '<li>Микроскопическое исследование осадка: содержание эритроцитов, лейкоцитов, эпителиальных клеток, цилиндров, бактерий и солей</li>' +
      '</ul><br>' +
      '<strong>При каких симптомах следует пройти обследование:</strong><br>' +
      '<ul>' +
      '<li>Боли в пояснице или внизу живота</li>' +
      '<li>Изменение цвета, прозрачности или запаха мочи</li>' +
      '<li>Учащенное или болезненное мочеиспускание</li>' +
      '<li>Отеки на лице, особенно под глазами</li>' +
      '<li>Повышение артериального давления</li>' +
      '</ul>');

    push('Биохимия крови', 'ежегодно', 'Оценка работы печени и почек', true,
      '<strong>Биохимический анализ крови</strong> позволяет:<br><br>' +
      '<strong>Оценить функцию внутренних органов:</strong> Анализ показывает состояние печени, почек, поджелудочной железы и других органов.<br><br>' +
      '<strong>Выявить нарушения обмена веществ:</strong> Помогает диагностировать сахарный диабет, подагру, нарушения липидного обмена.<br><br>' +
      '<strong>Контролировать лечение:</strong> При наличии хронических заболеваний биохимия помогает следить за эффективностью терапии.<br><br>' +
      '<strong>Биохимический анализ включает:</strong><br>' +
      '<ul>' +
      '<li>Глюкоза - оценка углеводного обмена, диагностика диабета</li>' +
      '<li>Мочевина и креатинин - оценка функции почек</li>' +
      '<li>АЛТ, АСТ, билирубин - оценка функции печени</li>' +
      '<li>Общий белок и белковые фракции - оценка белкового обмена</li>' +
      '<li>Холестерин и его фракции - оценка липидного обмена</li>' +
      '<li>Электролиты (калий, натрий, кальций) - оценка водно-электролитного баланса</li>' +
      '</ul><br>' +
      '<strong>При каких симптомах следует пройти обследование:</strong><br>' +
      '<ul>' +
      '<li>Постоянная жажда, сухость во рту</li>' +
      '<li>Тошнота, боли в правом подреберье</li>' +
      '<li>Отеки, особенно на ногах</li>' +
      '<li>Желтушность кожи и склер</li>' +
      '<li>Необъяснимая слабость, утомляемость</li>' +
      '</ul>');

    push('ЭКГ', age >= 40 ? 'ежегодно' : 'раз в 2 года', 'Проверка работы сердца', true,
      '<strong>Электрокардиограмма (ЭКГ)</strong> позволяет:<br><br>' +
      '<strong>Оценить электрическую активность сердца:</strong> ЭКГ регистрирует электрические импульсы, возникающие при работе сердца.<br><br>' +
      '<strong>Выявить нарушения ритма сердца:</strong> Помогает диагностировать аритмии, экстрасистолии, мерцательную аритмию.<br><br>' +
      '<strong>Диагностировать ишемическую болезнь сердца:</strong> Позволяет выявить признаки недостаточного кровоснабжения сердечной мышцы.<br><br>' +
      '<strong>Обнаружить перенесенный инфаркт миокарда:</strong> ЭКГ показывает характерные изменения при инфаркте.<br><br>' +
      '<strong>ЭКГ рекомендуется при:</strong><br>' +
      '<ul>' +
      '<li>Болях в груди, одышке, сердцебиении</li>' +
      '<li>Головокружениях, обмороках</li>' +
      '<li>Повышении артериального давления</li>' +
      '<li>Плановом обследовании лиц старше 40 лет</li>' +
      '<li>Наличии факторов риска сердечно-сосудистых заболеваний</li>' +
      '</ul><br>' +
      '<strong>При каких симптомах следует пройти обследование немедленно:</strong><br>' +
      '<ul>' +
      '<li>Сильная давящая боль за грудиной</li>' +
      '<li>Одышка в покое или при минимальной нагрузке</li>' +
      '<li>Нерегулярное сердцебиение с головокружением</li>' +
      '<li>Внезапная слабость, холодный пот</li>' +
      '</ul>');

    // Возрастные обследования
    push('Флюорография', 'ежегодно', 'Обследование легких', age >= 18,
      '<strong>Флюорография</strong> позволяет:<br><br>' +
      '<strong>Выявить заболевания легких:</strong> Рентгенологическое исследование помогает обнаружить туберкулез, опухоли легких, пневмонию.<br><br>' +
      '<strong>Обнаружить изменения в средостении:</strong> Позволяет выявить увеличение лимфатических узлов, опухоли средостения.<br><br>' +
      '<strong>Оценить состояние сердца и крупных сосудов:</strong> Флюорография показывает размеры и контуры сердца.<br><br>' +
      '<strong>Флюорография особенно важна для:</strong><br>' +
      '<ul>' +
      '<li>Курильщиков со стажем более 5 лет</li>' +
      '<li>Лиц с профессиональными вредностями (пыль, химические вещества)</li>' +
      '<li>Лиц с хроническими заболеваниями органов дыхания</li>' +
      '<li>Лиц с ослабленным иммунитетом</li>' +
      '<li>Всех взрослых в рамках профилактического обследования</li>' +
      '</ul><br>' +
      '<strong>При каких симптомах следует пройти обследование немедленно:</strong><br>' +
      '<ul>' +
      '<li>Длительный кашель (более 2-3 недель)</li>' +
      '<li>Боль в груди, особенно при дыхании</li>' +
      '<li>Одышка, не связанная с физической нагрузкой</li>' +
      '<li>Кровохарканье</li>' +
      '<li>Необъяснимая потеря веса, ночная потливость</li>' +
      '</ul>');

    push('УЗИ брюшной полости', 'раз в 1–2 года', 'Обследование внутренних органов', age >= 30,
      '<strong>Ультразвуковое исследование брюшной полости</strong> позволяет:<br><br>' +
      '<strong>Оценить состояние внутренних органов:</strong> УЗИ показывает размеры, структуру и положение печени, желчного пузыря, поджелудочной железы, селезенки, почек.<br><br>' +
      '<strong>Выявить патологические образования:</strong> Помогает обнаружить кисты, опухоли, камни в желчном пузыре и почках.<br><br>' +
      '<strong>Диагностировать воспалительные процессы:</strong> Позволяет выявить признаки панкреатита, холецистита, гепатита.<br><br>' +
      '<strong>Оценить состояние сосудов брюшной полости:</strong> Допплерография позволяет исследовать кровоток в сосудах.<br><br>' +
      '<strong>УЗИ брюшной полости рекомендуется при:</strong><br>' +
      '<ul>' +
      '<li>Болях в животе неясного происхождения</li>' +
      '<li>Нарушениях пищеварения (тошнота, изжога, вздутие)</li>' +
      '<li>Изменениях в анализах крови, указывающих на проблемы с печенью или поджелудочной железой</li>' +
      '<li>Подозрении на желчнокаменную болезнь</li>' +
      '<li>Плановом профилактическом обследовании</li>' +
      '</ul><br>' +
      '<strong>При каких симптомах следует пройти обследование немедленно:</strong><br>' +
      '<ul>' +
      '<li>Острая боль в правом подреберье</li>' +
      '<li>Желтушность кожи и склер</li>' +
      '<li>Рвота с примесью крови</li>' +
      '<li>Резкое увеличение объема живота</li>' +
      '</ul>');

    push('Маммография', 'каждые 1–2 года', 'Обследование молочных желез', gender === 'female' && age >= 40,
      '<strong>Маммография</strong> позволяет:<br><br>' +
      '<strong>Выявить ранние формы рака молочной железы:</strong> Рентгенологическое исследование помогает обнаружить опухоли на ранней стадии, когда они еще не прощупываются.<br><br>' +
      '<strong>Обнаружить доброкачественные образования:</strong> Помогает выявить кисты, фиброаденомы и другие доброкачественные изменения.<br><br>' +
      '<strong>Оценить состояние молочных желез:</strong> Позволяет определить тип строения молочных желез и выявить диффузные изменения.<br><br>' +
      '<strong>Контролировать динамику изменений:</strong> При наличии образований маммография помогает следить за их изменениями во времени.<br><br>' +
      '<strong>Маммография особенно важна для:</strong><br>' +
      '<ul>' +
      '<li>Женщин старше 40 лет</li>' +
      '<li>Женщин с наследственной предрасположенностью к рака молочной железы</li>' +
      '<li>Женщин с ранее выявленными доброкачественными образованиями</li>' +
      '<li>Женщин с жалобами на боли, уплотнения в молочных железах</li>' +
      '<li>Всех женщин в рамках профилактического обследования</li>' +
      '</ul><br>' +
      '<strong>При каких симптомах следует пройти обследование немедленно:</strong><br>' +
      '<ul>' +
      '<li>Обнаружение уплотнения в молочной железе</li>' +
      '<li>Выделения из соска, особенно кровянистые</li>' +
      '<li>Изменение формы или размера молочной железы</li>' +
      '<li>Втяжение соска или кожи</li>' +
      '<li>Появление "апельсиновой корки" на коже груди</li>' +
      '</ul>');

    push('Анализ на ПСА', 'ежегодно', 'Обследование предстательной железы', gender === 'male' && age >= 45,
      '<strong>Анализ на простат-специфический антиген (ПСА)</strong> позволяет:<br><br>' +
      '<strong>Выявить ранние формы рака предстательной железы:</strong> Анализ крови помогает обнаружить повышение уровня ПСА, которое может свидетельствовать о наличии опухоли.<br><br>' +
      '<strong>Дифференцировать доброкачественные и злокачественные заболевания простаты:</strong> Помогает отличить аденому простаты от рака.<br><br>' +
      '<strong>Контролировать лечение:</strong> При наличии рака простаты анализ ПСА помогает оценить эффективность лечения.<br><br>' +
      '<strong>Оценить состояние предстательной железы:</strong> Повышение ПСА может свидетельствовать о воспалении или других заболеваниях простаты.<br><br>' +
      '<strong>Анализ на ПСА особенно важен для:</strong><br>' +
      '<ul>' +
      '<li>Мужчин старше 45 лет</li>' +
      '<li>Мужчин с наследственной предрасположенностью к рака простаты</li>' +
      '<li>Мужчин с жалобами на нарушение мочеиспускания</li>' +
      '<li>Мужчин с ранее выявленными заболеваниями простаты</li>' +
      '<li>Всех мужчин в рамках профилактического обследования</li>' +
      '</ul><br>' +
      '<strong>При каких симптомах следует пройти обследование немедленно:</strong><br>' +
      '<ul>' +
      '<li>Затрудненное мочеиспускание</li>' +
      '<li>Частые позывы к мочеиспусканию, особенно ночью</li>' +
      '<li>Ощущение неполного опорожнения мочевого пузыря</li>' +
      '<li>Боль в промежности или нижней части живота</li>' +
      '<li>Кровь в моче или сперме</li>' +
      '</ul>');

    // Диспансеризация
    const currentYear = new Date().getFullYear();
    const dispanserizationYears = [1987, 1990, 1993, 1996, 1999, 2002, 2005, 2008];
    const needDispanserization = dispanserizationYears.includes(this.currentUser.birthYear) || age >= 40;

    if (needDispanserization) {
      push('Диспансеризация', age >= 40 ? 'ежегодно' : 'раз в 3 года', 'Комплексное обследование', true,
        '<strong>Диспансеризация</strong> — это бесплатное комплексное обследование, которое позволяет:<br><br>' +
        '<strong>Выявить заболевания на ранней стадии:</strong> Комплекс обследований помогает обнаружить болезни, когда они еще не проявляются симптомами.<br><br>' +
        '<strong>Оценить риск развития заболеваний:</strong> По результатам диспансеризации определяется группа здоровья и даются рекомендации по профилактике.<br><br>' +
        '<strong>Получить консультации специалистов:</strong> При выявлении отклонений пациент направляется к узким специалистам для дальнейшего обследования и лечения.<br><br>' +
        '<strong>Диспансеризация включает:</strong><br>' +
        '<ul>' +
        '<li>Анкетирование и опрос о жалобах</li>' +
        '<li>Измерение роста, веса, окружности талии, расчет ИМТ</li>' +
        '<li>Измерение артериального давления</li>' +
        '<li>Анализы крови (общий, биохимический, на холестерин и глюкозу)</li>' +
        '<li>Общий анализ мочи</li>' +
        '<li>Флюорографию или рентгенографию органов грудной клетки</li>' +
        '<li>ЭКГ</li>' +
        '<li>Осмотр терапевта с определением группы здоровья</li>' +
        (age >= 40 ? '<li>Измерение внутриглазного давления</li>' : '') +
        (age >= 40 && age <= 64 ? '<li>Анализ кала на скрытую кровь (2 раза)</li>' : '') +
        (age >= 45 ? '<li>Эзофагогастродуоденоскопию (однократно)</li>' : '') +
        (gender === 'female' && age >= 40 && age <= 75 ? '<li>Маммографию (раз в 2 года)</li>' : '') +
        (gender === 'male' && [45, 50, 55, 60, 64].includes(age) ? '<li>Анализ ПСА для мужчин</li>' : '') +
        '</ul><br>' +
        '<strong>Диспансеризация особенно важна при:</strong><br>' +
        '<ul>' +
        '<li>Наличии факторов риска (курение, избыточный вес, малоподвижный образ жизни)</li>' +
        '<li>Наследственной предрасположенности к заболеваниям</li>' +
        '<li>Возрасте старше 40 лет</li>' +
        '<li>Наличии хронических заболеваний</li>' +
        '<li>Профессиональных вредностях</li>' +
        '</ul>');
    }

    const block = document.getElementById('preventionList');
    block.innerHTML = plan.map(p => `
      <div class="prevention-item">
        <p>• <strong>${p.title}</strong> — ${p.freq}</p>
        <p class="prevention-note">${p.note || ''}</p>
        <button class="btn btn-secondary" onclick="HealthApp.toggleEventDetail('${p.title.replace(/\s+/g, '-')}')" style="width: auto; padding: 4px 8px; font-size: 12px; margin-top: 4px;">
          <i class="fas fa-info-circle"></i> Подробнее
        </button>
        <div id="event-detail-${p.title.replace(/\s+/g, '-')}" class="event-detail">
          ${p.detailedDescription || 'Описание отсутствует'}
        </div>
      </div>
    `).join('');

    const base = new Date();
    const newEvents = plan.map((p, index) => ({
      id: `${Date.now()}-${p.title}`,
      title: p.title,
      start: this.distributeDate(base, index, plan.length),
      desc: p.note,
      detailedDescription: p.detailedDescription
    }));

    this.events = this.mergeUpcoming(newEvents);
    localStorage.setItem('hcEvents', JSON.stringify(this.events));
    this.renderCalendarList();
    this.refreshMainStats();
  },

  // Распределение дат обследований
  distributeDate(baseDate, index, total) {
    const date = new Date(baseDate);
    const daysOffset = Math.floor((90 / total) * index);
    date.setDate(date.getDate() + daysOffset);
    return date;
  },

  // Добавление пользовательского события
  addCustomEvent() {
    const title = prompt('Введите название события:');
    if (title) {
      const dateStr = prompt('Введите дату (ГГГГ-ММ-ДД):');
      const date = dateStr ? new Date(dateStr) : new Date();

      const event = {
        id: `custom-${Date.now()}`,
        title: title,
        start: date,
        desc: 'Пользовательское событие',
        custom: true
      };

      this.events.push(event);
      localStorage.setItem('hcEvents', JSON.stringify(this.events));
      this.renderCalendarList();
      this.showNotification('Событие добавлено');
    }
  },

  // Отображение календаря
  renderCalendarList() {
    const list = document.getElementById('calendarList');
    if (!this.events.length) { list.innerHTML = '<li>Событий пока нет</li>'; return }
    list.innerHTML = this.events.slice(0, 20).map(e => {
      const d = new Date(e.start);
      return `<li>
        <div>
          <strong>${e.title}</strong>
          <div class="muted">${d.toLocaleDateString()}</div>
          <button class="btn btn-secondary" onclick="HealthApp.toggleEventDetail('${e.id}')" style="width: auto; padding: 4px 8px; font-size: 12px; margin-top: 4px;">
            <i class="fas fa-info-circle"></i> Для чего это обследование?
          </button>
          <div id="event-detail-${e.id}" class="event-detail">
            ${e.detailedDescription || e.desc || 'Описание отсутствует'}
          </div>
        </div>
        <div class="calendar-actions">
          <button class="btn" style="width:auto; padding:8px 12px" onclick="HealthApp.doneEvent('${e.id}')">
            <i class="fa-regular fa-circle-check"></i> Готово
          </button>
        </div>
      </li>`
    }).join('');
  },

  // Отметка события как выполненного
  doneEvent(id) {
    this.events = this.events.filter(e => e.id !== id);
    localStorage.setItem('hcEvents', JSON.stringify(this.events));
    this.renderCalendarList();
    this.refreshMainStats();
  },

  // Сброс выбора симптомов
  resetSymptomSelection() {
    const symptomSteps = document.getElementById('symptomSteps');
    symptomSteps.innerHTML = `
      <div class="card">
        <div class="card-header"><div class="card-title">Выберите область</div></div>
        <div class="symptom-option" onclick="selectSymptomArea('head','Голова')">
          <strong>Голова</strong>
          <div class="menu-description">Головная боль, головокружение, мигрень</div>
        </div>
        <div class="symptom-option" onclick="selectSymptomArea('chest','Грудь')">
          <strong>Грудь</strong>
          <div class="menu-description">Боль в груди, сердцебиение, одышка</div>
        </div>
        <div class="symptom-option" onclick="selectSymptomArea('stomach','Живот')">
          <strong>Живот</strong>
          <div class="menu-description">Боль в животе, расстройство, тошнота</div>
        </div>
        <div class="symptom-option" onclick="selectSymptomArea('joints','Суставы')">
          <strong>Суставы/Мышцы</strong>
          <div class="menu-description">Боль в суставах, мышцах, отеки</div>
        </div>
        <div class="symptom-option" onclick="selectSymptomArea('general','Общее состояние')">
          <strong>Общее состояние</strong>
          <div class="menu-description">Слабость, температура, утомляемость</div>
        </div>
      </div>
    `;
  },

  // Выбор области симптомов
  selectSymptomArea(symptom, name) {
    this.currentSymptom = symptom;

    // Детальный опрос для разных областей
    const questions = {
      head: [
        {q: "Опишите характер боли:", options: ["Пульсирующая", "Давящая", "Острая", "Тупая"]},
        {q: "Локализация боли:", options: ["Вся голова", "Лоб", "Виски", "Затылок"]},
        {q: "Сопровождается ли:", options: ["Тошнотой", "Светобоязнью", "Головокружением", "Нарушением зрения"]}
      ],
      chest: [
        {q: "Характер боли:", options: ["Давящая", "Жгучая", "Колющая", "Ноющая"]},
        {q: "Боль отдает в:", options: ["Левую руку", "Челюсть", "Спину", "Никуда не отдает"]},
        {q: "Сопровождается ли:", options: ["Одышкой", "Сердцебиением", "Потливостью", "Страхом"]}
      ],
      stomach: [
        {q: "Локализация боли:", options: ["Верх живота", "Низ живота", "Справа", "Слева"]},
        {q: "Характер боли:", options: ["Острая", "Тупая", "Схваткообразная", "Ноющая"]},
        {q: "Связь с приемом пищи:", options: ["Усиливается после еды", "Ослабевает после еды", "Не связано", "На голодный желудок"]}
      ],
      joints: [
        {q: "Какие суставы болят:", options: ["Коленные", "Тазобедренные", "Плечевые", "Мелкие суставы кистей"]},
        {q: "Есть ли:", options: ["Отечность", "Покраснение", "Ограничение движений", "Утренняя скованность"]},
        {q: "Боль усиливается:", options: ["При движении", "В покое", "Ночью", "При изменении погоды"]}
      ],
      general: [
        {q: "Общее самочувствие:", options: ["Слабость", "Повышенная утомляемость", "Сонливость", "Раздражительность"]},
        {q: "Температура тела:", options: ["Нормальная", "37-38°C", "Выше 38°C", "Пониженная"]},
        {q: "Аппетит:", options: ["Нормальный", "Снижен", "Повышен", "Отсутствует"]}
      ]
    };

    const specialists = {
      head: "Невролог, офтальмолог, терапевт",
      chest: "Кардиолог, пульмонолог, терапевт",
      stomach: "Гастроэнтеролог, терапевт, хирург",
      joints: "Ревматолог, ортопед, терапевт",
      general: "Терапевт, эндокринолог"
    };

    let html = `<div class="card">
      <div class="card-header">
        <div class="card-title">${name}</div>
        <button class="back-button" onclick="resetSymptomSelection()" style="margin:0"><i class="fas fa-arrow-left"></i> Назад</button>
      </div>`;

    html += `<div class="symptom-question">
      <p><strong>Ответьте на вопросы о ваших симптомах:</strong></p>
    </div>`;

    questions[symptom].forEach((questionObj, i) => {
      html += `<div class="form-group">
        <label class="form-label">${i + 1}. ${questionObj.q}</label>`;

      questionObj.options.forEach(option => {
        html += `<div style="margin: 4px 0;">
          <input type="radio" id="${symptom}-q${i}-${option}" name="${symptom}-q${i}" value="${option}">
          <label for="${symptom}-q${i}-${option}" style="margin-left: 8px;">${option}</label>
        </div>`;
      });

      html += `</div>`;
    });

    html += `<div class="recommendation-card">
      <strong>💡 Рекомендуемые специалисты:</strong>
      <p>${specialists[symptom]}</p>
      <div class="inline" style="margin-top:8px">
        <button class="btn btn-primary" onclick="showScreen('clinicsScreen')">
          <i class="fas fa-hospital"></i> Найти клинику
        </button>
        <button class="btn btn-secondary" onclick="resetSymptomSelection()">
          <i class="fas fa-redo"></i> Новый симптом
        </button>
      </div>
    </div></div>`;

    document.getElementById('symptomSteps').innerHTML = html;
  },

  // Вычисление оценки здоровья
  computeWellness() {
    let score = parseInt(localStorage.getItem('surveyScore') || '50');
    const last = this.healthData[this.healthData.length - 1];
    if (last) {
      if (last.syst && last.diast) {
        const s = last.syst, d = last.diast;
        if (s > 180 || d > 110) score += 25;
        else if (s > 160 || d > 100) score += 15;
        else if (s > 140 || d > 90) score += 8;
        else if (s >= 110 && d >= 70 && s <= 130 && d <= 85) score -= 8;
      }
      if (last.glucose) {
        if (last.glucose >= 7) score += 15;
        else if (last.glucose >= 5.6) score += 6;
        else if (last.glucose >= 4 && last.glucose <= 5.5) score -= 5;
      }
      if (last.sleep) {
        if (last.sleep < 6) score += 6;
        else if (last.sleep > 9.5) score += 3;
        else score -= 2;
      }
    }
    score = Math.max(0, Math.min(100, score));
    let label = 'Среднее', color = 'var(--warning)';
    if (score <= 35) { label = 'Отличное'; color = 'var(--success)' }
    else if (score <= 65) { label = 'Хорошее'; color = 'var(--accent)' }
    else if (score <= 85) { label = 'Удовлетворительное'; color = 'var(--warning)' }
    else { label = 'Низкое'; color = 'var(--danger)' }
    return { score, label, color };
  },

  // Обновление главной статистики
  refreshMainStats() {
    const { score, label, color } = this.computeWellness();
    const ws = document.getElementById('wellnessScore');
    ws.textContent = `${100 - Math.round(score)}%`;
    ws.style.color = color;

    const next = this.getNextEvent();
    const daysEl = document.getElementById('nextEventDays');
    const prev = document.getElementById('upcomingPreview');
    if (next) {
      const diff = Math.ceil((next.start - new Date()) / 86400000);
      daysEl.textContent = diff >= 0 ? diff : 0;
      prev.innerHTML = `
        <div onclick="HealthApp.showEventDetail('${next.id}')" style="cursor: pointer; padding: 10px; border: 1px solid var(--border); border-radius: 8px;">
          <p><strong>${next.title}</strong> — ${next.start.toLocaleDateString()} (${diff >= 0 ? `через ${diff} дн.` : 'сегодня'})</p>
          <div class="progress-bar"><div class="progress-fill" style="width:${Math.min(100, Math.max(0, (1 - diff / 30) * 100))}%"></div></div>
          <p class="muted" style="margin-top: 8px; font-size: 12px;">Нажмите для подробной информации</p>
        </div>
      `;
    } else {
      daysEl.textContent = '—';
      prev.textContent = 'Нет запланированных событий'
    }
  },

  // Получение следующего события
  getNextEvent() {
    return (this.events || []).map(e => ({ ...e, start: new Date(e.start) })).find(e => e.start >= new Date()) || null;
  },

  // Получение данных для графиков
  getSeries() {
    const labels = this.healthData.map(e => new Date(e.date).toLocaleDateString());
    return {
      labels,
      weight: this.healthData.map(e => e.weight || null),
      syst: this.healthData.map(e => e.syst || null),
      diast: this.healthData.map(e => e.diast || null),
      glucose: this.healthData.map(e => e.glucose || null),
      steps: this.healthData.map(e => e.steps || null),
      sleep: this.healthData.map(e => e.sleep || null),
      pulse: this.healthData.map(e => e.pulse || null)
    }
  },

  // Отрисовка графиков
  renderChart(type) {
    const ctx = document.getElementById('healthChart').getContext('2d');
    if (this._chart) this._chart.destroy();
    const s = this.getSeries();
    const dsMap = {
      weight: [{ label: 'Вес (кг)', data: s.weight, borderColor: '#4CAF50', backgroundColor: 'rgba(76, 175, 80, .1)' }],
      glucose: [{ label: 'Глюкоза (ммоль/л)', data: s.glucose, borderColor: '#3f51b5', backgroundColor: 'rgba(63,81,181,.1)' }],
      steps: [{ label: 'Шаги', data: s.steps, borderColor: '#ff9800', backgroundColor: 'rgba(255,152,0,.1)' }],
      sleep: [{ label: 'Сон (ч)', data: s.sleep, borderColor: '#009688', backgroundColor: 'rgba(0,150,136,.1)' }],
      pulse: [{ label: 'Пульс (уд/мин)', data: s.pulse, borderColor: '#9c27b0', backgroundColor: 'rgba(156,39,176,.1)' }],
      bp: [
        { label: 'Систолическое давление', data: s.syst, borderColor: '#e91e63', backgroundColor: 'rgba(233,30,99,.1)' },
        { label: 'Диастолическое давление', data: s.diast, borderColor: '#795548', backgroundColor: 'rgba(121,85,72,.1)' }
      ]
    };
    this._chart = new Chart(ctx, {
      type: 'line',
      data: { labels: s.labels, datasets: dsMap[type] || dsMap.weight },
      options: { responsive: true, plugins: { legend: { display: true } }, spanGaps: true }
    });
  },

  // Привязка Госуслуг
  linkGosuslugi() {
    this.isGosLinked = true;
    localStorage.setItem('gosLinked', 'true');
    this.showNotification('Кабинет «Госуслуги.Здоровье» привязан. Импортированы прививки и полис ОМС (демо).');
    this.updateUIWithUserData();
  },

  // Отключение Госуслуг
  unlinkGosuslugi() {
    this.isGosLinked = false;
    localStorage.setItem('gosLinked', 'false');
    this.showNotification('Привязка «Госуслуги.Здоровье» отключена');
    this.updateUIWithUserData();
  },

  // Звонок в клинику
  callClinic(phone) { this.showNotification(`Имитация звонка на ${phone}`) },

  // Показать клинику на карте
  showClinicOnMap() { this.showNotification('Открываем карту с расположением клиник…') },

  // Экстренная помощь
  showEmergencyAlert() {
    const msg = this.currentUser && this.currentUser.emergencyContact ?
      `ЭКСТРЕННАЯ ПОМОЩЬ\n\nТелефон: 103 или 112\n\nУведомить: ${this.currentUser.emergencyContact}?` :
      'ЭКСТРЕННАЯ ПОМОЩЬ\n\nТелефон: 103 или 112\n\nВызываем скорую?';
    if (confirm(msg)) this.showNotification('Вызов экстренных служб…');
  },

  // Выход из системы
  logout() {
    if (confirm('Выйти из профиля?')) {
      localStorage.removeItem('healthCompassUser');
      this.currentUser = null;
      this.showScreen('profileScreen');
      this.showNotification('Вы вышли из системы');
    }
  },

  // Переключение тумблера
  toggleSwitch(el) { el.classList.toggle('active') },

  // Показать уведомление
  showNotification(text) {
    const n = document.createElement('div');
    n.className = 'notification';
    n.textContent = text;
    document.body.appendChild(n);
    setTimeout(() => {
      if (n.parentNode) {
        n.parentNode.removeChild(n);
      }
    }, 3000);
  },

  // Объединение событий
  mergeUpcoming(newEvents) {
    const now = new Date();
    const future = (this.events || []).filter(e => new Date(e.start) > now);
    const unique = [...future];
    newEvents.forEach(e => {
      const has = future.some(x => x.title === e.title && Math.abs(new Date(x.start) - e.start) < 1000 * 60 * 60 * 24 * 20);
      if (!has) unique.push(e);
    });
    return unique.sort((a, b) => new Date(a.start) - new Date(b.start));
  },

  // Экспорт в ICS
  exportICS() {
    const lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//HealthCompass//RU'];
    (this.events || []).forEach(e => {
      const dt = new Date(e.start);
      const pad = n => String(n).padStart(2, '0');
      const dtstamp = `${dt.getUTCFullYear()}${pad(dt.getUTCMonth() + 1)}${pad(dt.getUTCDate())}T${pad(dt.getUTCHours())}${pad(dt.getUTCMinutes())}00Z`;
      lines.push('BEGIN:VEVENT');
      lines.push(`UID:${e.id}@hc`);
      lines.push(`DTSTAMP:${dtstamp}`);
      lines.push(`DTSTART:${dtstamp}`);
      lines.push(`SUMMARY:${e.title}`);
      if (e.desc) lines.push(`DESCRIPTION:${e.desc}`);
      lines.push('END:VEVENT');
    });
    lines.push('END:VCALENDAR');
    const blob = new Blob([lines.join('\n')], { type: 'text/calendar' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'healthcompass.ics'; a.click(); URL.revokeObjectURL(url);
  },

  // Очистка дневника
  clearDiary() {
    if (confirm('Очистить все записи дневника?')) {
      this.healthData = [];
      localStorage.setItem('healthData', '[]');
      this.renderChart('weight');
      this.refreshMainStats();
      this.updateDailyRecommendations();
    }
  }
};

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
  HealthApp.init();

  // Обработчик опросника
  const surveyForm = document.getElementById('surveyForm');
  if (surveyForm) {
    surveyForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const fd = new FormData(surveyForm);
      const sum = ['energy', 'sleepQ', 'stress', 'activity', 'diet', 'habits', 'symptoms'].reduce((acc, k) => acc + Number(fd.get(k) || 0), 0);
      const norm = Math.round((sum / 21) * 100);
      localStorage.setItem('surveyScore', String(norm));

      const r = HealthApp.computeWellness();
      const resultEl = document.getElementById('surveyResult');
      if (resultEl) {
        resultEl.innerHTML = `
          <div class="card">
            <div class="card-header"><div class="card-title">Результат</div></div>
            <p><strong>Оценка:</strong> ${100 - r.score}% (${r.label})</p>
            <p class="muted">Рекомендация: соблюдайте умеренность в обследованиях, ориентируйтесь на показания и план, работайте со стрессом и сном.</p>
          </div>`;
      }
      HealthApp.refreshMainStats();
    });
  }
});

// Fallback на случай если DOM уже загружен
if (document.readyState !== 'loading') {
  HealthApp.init();
}