from models import db, User, Topic, Test, UsersFormulas, Modul, Achievement
from datetime import datetime, timedelta

ACHIEVEMENTS = {
    "Начинающий физик": "Вы прошли свою первую тему и освоили 5 формул.",
    "Скоростной решатель": "Вы решили тест меньше чем за минуту.",
    "Физик-перфекционист": "Вы решили тест с первого раза без единой ошибки.",
    "Мастер Энергии": "Вы успешно прошли все темы и задачи, связанные с энергией и работой.",
    "Кинематический гений": "Вы решили тест по кинематике на 100%.",
    "Динамический мастер": "Вы решили тест по динамике на 100%.",
    "Статистический эксперт": "Вы решили тест по статике на 100%.",
    "Энергетический виртуоз": "Вы решили тест по энергетике на 100%.",
    "Термофизический специалист": "Вы решили тест по термофизике на 100%.",
    "Формульный коллекционер": "Вы освоили 20 различных формул.",
    "Тестовый марафонец": "Вы прошли 10 тестов за один день.",
    "Недельный стрик": "Вы проходили тесты каждый день в течение недели."
}

def check_achievements(user_id):
    user = User.query.get(user_id)
    if not user:
        return

    # "Начинающий физик": первая тема и 5 формул
    if Topic.query.filter_by(user_id=user_id).count() >= 1 and UsersFormulas.query.filter_by(iduser=user_id).count() >= 5:
        add_achievement(user_id, "Начинающий физик")

    # "Скоростной решатель": тест меньше чем за минуту
    last_test = Test.query.filter_by(user_id=user_id).order_by(Test.end_time.desc()).first()
    if last_test and (last_test.end_time - last_test.start_time).total_seconds() < 60:
        add_achievement(user_id, "Скоростной решатель")

    # "Физик-перфекционист": тест на 100% с первой попытки
    if last_test and last_test.success_rate == 100 and Test.query.filter_by(user_id=user_id, section=last_test.section).count() == 1:
        add_achievement(user_id, "Физик-перфекционист")

    # "Мастер Энергии": все темы по энергетике на 80%+
    energy_module = Modul.query.filter_by(name="Энергетика").first()
    if energy_module:
        energy_topics = Topic.query.filter_by(user_id=user_id, name=energy_module.name).all()
        if energy_topics and all(topic.success_rate >= 80 for topic in energy_topics):
            add_achievement(user_id, "Мастер Энергии")

    # "Кинематический гений": тест по кинематике на 100%
    kinematics_test = Test.query.filter_by(user_id=user_id, section="Кинематика", success_rate=100).first()
    if kinematics_test:
        add_achievement(user_id, "Кинематический гений")

    # "Динамический мастер": тест по динамике на 100%
    dynamics_test = Test.query.filter_by(user_id=user_id, section="Динамика", success_rate=100).first()
    if dynamics_test:
        add_achievement(user_id, "Динамический мастер")

    # "Статистический эксперт": тест по статике на 100%
    statics_test = Test.query.filter_by(user_id=user_id, section="Статика", success_rate=100).first()
    if statics_test:
        add_achievement(user_id, "Статистический эксперт")

    # "Энергетический виртуоз": тест по энергетике на 100%
    energy_test = Test.query.filter_by(user_id=user_id, section="Энергетика", success_rate=100).first()
    if energy_test:
        add_achievement(user_id, "Энергетический виртуоз")

    # "Термофизический специалист": тест по термофизике на 100%
    thermo_test = Test.query.filter_by(user_id=user_id, section="Термофизика", success_rate=100).first()
    if thermo_test:
        add_achievement(user_id, "Термофизический специалист")

    # "Формульный коллекционер": освоено 20 формул
    if UsersFormulas.query.filter_by(iduser=user_id).count() >= 20:
        add_achievement(user_id, "Формульный коллекционер")

    # "Тестовый марафонец": 10 тестов за день
    today = datetime.now().date()
    tests_today = Test.query.filter_by(user_id=user_id).filter(Test.date == today).count()
    if tests_today >= 10:
        add_achievement(user_id, "Тестовый марафонец")

    # "Недельный стрик": тесты каждый день в течение недели
    week_ago = datetime.now().date() - timedelta(days=6)
    daily_tests = db.session.query(db.func.distinct(db.func.date(Test.date))).filter(
        Test.user_id == user_id,
        Test.date >= week_ago
    ).count()
    if daily_tests >= 7:
        add_achievement(user_id, "Недельный стрик")

def add_achievement(user_id, achievement_name):
    if not Achievement.query.filter_by(user_id=user_id, achievement_name=achievement_name).first():
        new_achievement = Achievement(
            user_id=user_id,
            achievement_name=achievement_name,
            achievement_description=ACHIEVEMENTS[achievement_name]
        )
        db.session.add(new_achievement)
        db.session.commit()