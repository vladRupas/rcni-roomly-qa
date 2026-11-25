const form = document.querySelector('#booking-form');
const status = document.querySelector('#form-status');
const dateInput = document.querySelector('#date');

const capacities = { small: 4, medium: 10, large: 20 };
const roomNames = { small: 'Малая', medium: 'Средняя', large: 'Большая' };

function localDateString(date = new Date()) {
  const offset = date.getTimezoneOffset();
  return new Date(date.getTime() - offset * 60 * 1000).toISOString().slice(0, 10);
}

dateInput.min = localDateString();

function setError(name, message) {
  const field = document.querySelector(`[name="${name}"]`).closest('.field');
  field.classList.toggle('has-error', Boolean(message));
  field.querySelector('.field-error').textContent = message || '';
}

function clearErrors() {
  document.querySelectorAll('.field').forEach((field) => field.classList.remove('has-error'));
  document.querySelectorAll('.field-error').forEach((error) => { error.textContent = ''; });
  status.className = 'form-status';
  status.textContent = '';
}

function validate(data) {
  const errors = {};
  if (!data.room) errors.room = 'Выберите комнату.';
  if (!data.date) errors.date = 'Укажите дату.';
  if (!data.startTime) errors.startTime = 'Укажите время начала.';
  if (!data.endTime) errors.endTime = 'Укажите время окончания.';
  if (!data.participants) errors.participants = 'Укажите количество участников.';
  if (!data.name.trim()) errors.name = 'Укажите имя.';
  if (!data.email.trim()) errors.email = 'Укажите рабочую почту.';

  if (data.date && data.date < dateInput.min) errors.date = 'Дата не может быть в прошлом.';

  if (data.startTime && data.endTime && data.endTime < data.startTime) {
    errors.endTime = 'Время окончания должно быть позже начала.';
  }

  if (data.room && data.participants && Number(data.participants) > capacities[data.room]) {
    errors.participants = `В комнате максимум ${capacities[data.room]} участника.`;
  }

  if (data.participants && (Number(data.participants) < 1 || Number(data.participants) > 20)) {
    errors.participants = 'Количество участников — от 1 до 20.';
  }

  if (data.email && !/^\S+@\S+\.\S+$/.test(data.email)) {
    errors.email = 'Введите корректную рабочую почту.';
  }

  return errors;
}

function formatTime(value) {
  return value || '—';
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  clearErrors();

  const data = Object.fromEntries(new FormData(form).entries());
  const errors = validate(data);
  Object.entries(errors).forEach(([name, message]) => setError(name, message));

  if (Object.keys(errors).length) {
    status.className = 'form-status error';
    status.textContent = 'Проверьте, пожалуйста, заполнение формы.';
    return;
  }

  status.className = 'form-status success';
  status.innerHTML = `<strong>Бронирование создано.</strong><br>${roomNames[data.room]}, ${data.date}, ${formatTime(data.startTime)}–${formatTime(data.endTime)} · ${data.name}`;
});

form.addEventListener('input', (event) => {
  const name = event.target.name;
  if (!name) return;
  setError(name, '');
  if (status.classList.contains('error')) {
    status.className = 'form-status';
    status.textContent = '';
  }
});
