import argparse
import django
import os
import random
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()
from datacenter.models import Schoolkid, Mark, Chastisement, Subject, Lesson, Commendation


COMMENDATIONS = [
    'Молодец!',
    'Отлично!',
    'Хорошо!',
    'Гораздо лучше, чем я ожидал!',
    'Ты меня приятно удивил!',
    'Великолепно!',
    'Прекрасно!',
    'Ты меня очень обрадовал!',
    'Именно этого я давно ждал от тебя!',
    'Сказано здорово – просто и ясно!',
    'Ты, как всегда, точен!',
    'Очень хороший ответ!',
    'Талантливо!',
    'Ты сегодня прыгнул выше головы!',
    'Я поражен!',
    'Уже существенно лучше!',
    'Потрясающе!',
    'Замечательно!',
    'Прекрасное начало!',
    'Так держать!',
    'Ты на верном пути!',
    'Здорово!',
    'Это как раз то, что нужно!',
    'Я тобой горжусь!',
    'С каждым разом у тебя получается всё лучше!',
    'Мы с тобой не зря поработали!',
    'Я вижу, как ты стараешься!',
    'Ты растешь над собой!',
    'Ты многое сделал, я это вижу!',
    'Теперь у тебя точно все получится!'
]


def fix_marks(schoolkid: Schoolkid):
    schoolkid_bad_marks = Mark.objects.filter(schoolkid=schoolkid, points__lte=3)

    for mark in schoolkid_bad_marks:
        mark.points = 5
        mark.save()


def remove_chastisements(schoolkid: Schoolkid):
    schoolkid_chastisements = Chastisement.objects.filter(schoolkid=schoolkid)
    schoolkid_chastisements.delete()


def create_commendation(schoolkid: Schoolkid, subject_title: str):
    text = random.choice(COMMENDATIONS)
    subject = Subject.objects.filter(
        title=subject_title, 
        year_of_study=schoolkid.year_of_study
    ).first()
    if not subject:
        print(f'Уточните название предмета. Предмет {subject_title} не найден.')
        return
    lesson = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study, 
        group_letter=schoolkid.group_letter, 
        subject=subject
    ).order_by('-date').first()
    if not lesson:
        print(f'Уточните название предмета и ученика. Предмет {subject_title} для ученика {schoolkid} не найден.')
        return
    teacher = lesson.teacher
    created = lesson.date

    Commendation.objects.create(text=text, 
                                created=created, 
                                schoolkid=schoolkid, 
                                subject=subject, 
                                teacher=teacher)
    

def main():
    parser = argparse.ArgumentParser(description='Редактирование школьной БД')
    parser.add_argument("action", choices=["fix_marks", "remove_chastisements", "create_commendation"],
                        help="Выберите действие: fix_marks, remove_chastisements или create_commendation")
    parser.add_argument("name", nargs='?', help="Имя ученика", default=None)
    parser.add_argument("--subject", nargs='?', help="Предмет (только для create_commendation)", default=None)

    args = parser.parse_args()

    if not args.name:
        print('Ошибка: Укажите имя ученика.')
        return

    schoolkids = Schoolkid.objects.filter(full_name__icontains=args.name)
    if not schoolkids.exists():
        print(f'Ошибка: Ученик с именем {args.name} не найден.')
        return
    
    if len(schoolkids) > 1:
        print(f'Ошибка: Найдено несколько учеников с именем {args.name}.')
        return

    schoolkid = schoolkids.first()
        
    if args.action == "fix_marks":
        fix_marks(schoolkid)
    elif args.action == "remove_chastisements":
        remove_chastisements(schoolkid)
    elif args.action == "create_commendation":
        if not args.subject:
            print("Ошибка: Для create_commendation требуется указать предмет через --subject")
            return
        create_commendation(schoolkid, args.subject)


if __name__ == '__main__':
    main()