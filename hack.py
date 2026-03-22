import random

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from datacenter.models import (
    Chastisement,
    Commendation,
    Lesson,
    Mark,
    Schoolkid,
    Subject,
)


def fix_marks(schoolkid_name):
	marks = Mark.objects.filter(
		schoolkid__full_name__contains=schoolkid_name, 
		points__lt=4
	)
	for mark in marks:
		mark.points = 5
		mark.save()


def remove_chastisements(schoolkid_name):
	chastisements = Chastisement.objects.filter(
		schoolkid__full_name__contains=schoolkid_name
	)
	for chastisement in chastisements:
		chastisement.delete()


def create_commedation(schoolkid_name, subject_title):
	try:
		child = Schoolkid.objects.get(full_name__contains=schoolkid_name)
	except ObjectDoesNotExist:
		print(f"Ошибка: Ученик '{schoolkid_name}' не найден.")
		return
	except MultipleObjectsReturned:
		print(f"Ошибка: Найдено несколько учеников с именем '{schoolkid_name}'")
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

	commendation_variants = [
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
	
	Commendation.objects.create(
		text=random.choice(commendation_variants),
		created=target_lesson.date,
		schoolkid=child,
		subject=subject,
		teacher=target_lesson.teacher
	)
