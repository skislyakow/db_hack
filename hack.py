import random

from datacenter.models import (
    Chastisement,
    Commendation,
    Lesson,
    Mark,
    Schoolkid,
    Subject,
)


COMMENDATIONS = [
    'Молодец!', 
	'Отлично!', 
	'Хорошо!', 
	'Гораздо лучше, чем я ожидал!',
    'Ты меня приятно удивил!', 
	'Великолепно!', 
	'Прекрасно!',
    'Очень хороший ответ!', 
	'Талантливо!', 
	'Уже существенно лучше!',
    'Потрясающе!', 
	'Замечательно!', 
	'Прекрасное начало!',
    'Так держать!', 
	'Ты на правильном пути!', 
	'Здорово!',
    'Это как раз то, что нужно!', 
	'Я тобой горжусь!',
    'С каждым разом у тебя получается всё лучше!',
    'Мы с тобой обязательно договоримся!',
    'Я вижу, как ты стараешься!', 
	'Ты растешь над собой!',
    'Ты многое сделал, я это вижу!', 
	'Теперь твои успехи станут заметными всем!',
]


def get_schoolkid(name):
    try:
        return Schoolkid.objects.get(full_name__contains=name)
    except Schoolkid.DoesNotExist:
        print(f"Ошибка: Ученик '{name}' не найден.")
        return None
    except Schoolkid.MultipleObjectsReturned:
        raise ValueError(
            f"Ошибка: Найдено несколько учеников с именем '{name}'"
        )


def fix_marks(schoolkid_name):
	child = get_schoolkid(schoolkid_name)
	if child:
		Mark.objects.filter(schoolkid=child, points__lt=4).update(points=5)


def remove_chastisements(schoolkid_name):
	child = get_schoolkid(schoolkid_name)
	if child:
		Chastisement.objects.filter(schoolkid=child).delete()


def create_commendation(schoolkid_name, subject_title):
	child = get_schoolkid(schoolkid_name)
	if not child:
		return
	
	subject = Subject.objects.filter(
		title__contains=subject_title,
		year_of_study=child.year_of_study
	).first()

	already_commended = Commendation.objects.filter(
		schoolkid=child,
		subject=subject
	).values_list('created', flat=True)

	available_for_commendations = Lesson.objects.filter(
		year_of_study=child.year_of_study,
		group_letter=child.group_letter,
		subject=subject
	).exclude(date__in=already_commended).order_by('-date')

	target_lesson = available_for_commendations.first()

	if not target_lesson:
		raise ValueError(
			f"У ученика {child.full_name} нет уроков по предмету '{subject_title}'."
		)
	
	Commendation.objects.create(
		text=random.choice(COMMENDATIONS),
		created=target_lesson.date,
		schoolkid=child,
		subject=subject,
		teacher=target_lesson.teacher
	)
