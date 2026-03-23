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


class SchoolkidError(Exception):
	pass


class LessonNotFoundError(Exception):
    pass


def fix_marks(schoolkid_name):
	marks = Mark.objects.filter(
		schoolkid__full_name__contains=schoolkid_name, 
		points__lt=4
	).update(points=5)


def remove_chastisements(schoolkid_name):
	chastisements = Chastisement.objects.filter(
		schoolkid__full_name__contains=schoolkid_name
	).delete()


def create_commendation(schoolkid_name, subject_title):
	try:
		child = Schoolkid.objects.get(full_name__contains=schoolkid_name)
	except Schoolkid.DoesNotExist:
		print(f"Ошибка: Ученик '{schoolkid_name}' не найден.")
		return None
	except Schoolkid.MultipleObjectsReturned:
		raise SchoolkidError(
			f"Ошибка: Найдено несколько учеников с именем '{schoolkid_name}'"
		)
	
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
		raise LessonNotFoundError(
			f"У ученика {child.full_name} нет уроков по предмету '{subject_title}'."
		)
	
	Commendation.objects.create(
		text=random.choice(COMMENDATIONS),
		created=target_lesson.date,
		schoolkid=child,
		subject=subject,
		teacher=target_lesson.teacher
	)
