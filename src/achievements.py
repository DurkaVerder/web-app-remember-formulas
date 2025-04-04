from models import db, User, Topic, Test, UsersFormulas, Modul, Achievement
from datetime import datetime, timedelta
from logger import log_info, log_error, log_debug

ACHIEVEMENTS = {
    "Начинающий физик": {
        "description": "Вы прошли свою первую тему и освоили 5 формул.",
        "image_path": "/static/achievements/beginner_physicist.png"
    },
    "Скоростной решатель": {
        "description": "Вы решили тест меньше чем за минуту.",
        "image_path": "/static/achievements/speed_solver.png"
    },
    "Физик-перфекционист": {
        "description": "Вы решили тест с первого раза без единой ошибки.",
        "image_path": "/static/achievements/perfectionist.png"
    },
    "Мастер Энергии": {
        "description": "Вы успешно прошли все темы и задачи, связанные с энергией и работой.",
        "image_path": "/static/achievements/energy_master.png"
    },
    "Кинематический гений": {
        "description": "Вы решили тест по кинематике на 100%.",
        "image_path": "/static/achievements/kinematics_genius.png"
    },
    "Динамический мастер": {
        "description": "Вы решили тест по динамике на 100%.",
        "image_path": "/static/achievements/dynamics_master.png"
    },
    "Статистический эксперт": {
        "description": "Вы решили тест по статике на 100%.",
        "image_path": "/static/achievements/statics_expert.png"
    },
    "Энергетический виртуоз": {
        "description": "Вы решили тест по энергетике на 100%.",
        "image_path": "/static/achievements/energy_virtuoso.png"
    },
    "Термофизический специалист": {
        "description": "Вы решили тест по термофизике на 100%.",
        "image_path": "/static/achievements/thermophysics_specialist.png"
    },
    "Формульный коллекционер": {
        "description": "Вы освоили 20 различных формул.",
        "image_path": "/static/achievements/formula_collector.png"
    },
    "Тестовый марафонец": {
        "description": "Вы прошли 10 тестов за один день.",
        "image_path": "/static/achievements/test_marathoner.png"
    },
    "Недельный стрик": {
        "description": "Вы проходили тесты каждый день в течение недели.",
        "image_path": "/static/achievements/weekly_streak.png"
    }
}

def check_achievements(user_id):
    log_info(f"Checking achievements for user {user_id}")
    try:
        user = User.query.get(user_id)
        if not user:
            return

        # "Начинающий физик": первая тема и 5 формул
        if Topic.query.filter_by(user_id=user_id).count() >= 1 and UsersFormulas.query.filter_by(iduser=user_id).count() >= 5:
            add_achievement(user_id, "Начинающий физик")
            log_info(f"User {user_id} qualifies for 'Начинающий физик' (Topics: {topics_count}, Formulas: {formulas_count})")

        # "Скоростной решатель": тест меньше чем за минуту
        last_test = Test.query.filter_by(user_id=user_id).order_by(Test.end_time.desc()).first()
        if last_test and (last_test.end_time - last_test.start_time).total_seconds() < 60:
            add_achievement(user_id, "Скоростной решатель")
            log_info(f"User {user_id} qualifies for 'Скоростной решатель' (Test time: {(last_test.end_time - last_test.start_time).total_seconds()} seconds)")

        # "Физик-перфекционист": тест на 100% с первой попытки
        if last_test and last_test.success_rate == 100 and Test.query.filter_by(user_id=user_id, section=last_test.section).count() == 1:
            add_achievement(user_id, "Физик-перфекционист")
            log_info(f"User {user_id} qualifies for 'Физик-перфекционист' (Section: {last_test.section})")

        # "Мастер Энергии": все темы по энергетике на 80%+
        energy_module = Modul.query.filter_by(name="Энергетика").first()
        if energy_module:
            energy_topics = Topic.query.filter_by(user_id=user_id, name=energy_module.name).all()
            if energy_topics and all(topic.success_rate >= 80 for topic in energy_topics):
                add_achievement(user_id, "Мастер Энергии")
                log_info(f"User {user_id} qualifies for 'Мастер Энергии' (Energy topics count: {len(energy_topics)})")

        # "Кинематический гений": тест по кинематике на 100%
        kinematics_test = Test.query.filter_by(user_id=user_id, section="Кинематика", success_rate=100).first()
        if kinematics_test:
            add_achievement(user_id, "Кинематический гений")
            log_info(f"User {user_id} qualifies for 'Кинематический гений'")

        # "Динамический мастер": тест по динамике на 100%
        dynamics_test = Test.query.filter_by(user_id=user_id, section="Динамика", success_rate=100).first()
        if dynamics_test:
            add_achievement(user_id, "Динамический мастер")
            log_info(f"User {user_id} qualifies for 'Динамический мастер'")

        # "Статистический эксперт": тест по статике на 100%
        statics_test = Test.query.filter_by(user_id=user_id, section="Статика", success_rate=100).first()
        if statics_test:
            add_achievement(user_id, "Статистический эксперт")
            log_info(f"User {user_id} qualifies for 'Статистический эксперт'")

        # "Энергетический виртуоз": тест по энергетике на 100%
        energy_test = Test.query.filter_by(user_id=user_id, section="Энергетика", success_rate=100).first()
        if energy_test:
            add_achievement(user_id, "Энергетический виртуоз")
            log_info(f"User {user_id} qualifies for 'Энергетический виртуоз'")

        # "Термофизический специалист": тест по термофизике на 100%
        thermo_test = Test.query.filter_by(user_id=user_id, section="Термофизика", success_rate=100).first()
        if thermo_test:
            add_achievement(user_id, "Термофизический специалист")
            log_info(f"User {user_id} qualifies for 'Термофизический специалист'")

        # "Формульный коллекционер": освоено 20 формул
        if UsersFormulas.query.filter_by(iduser=user_id).count() >= 20:
            add_achievement(user_id, "Формульный коллекционер")
            log_info(f"User {user_id} qualifies for 'Формульный коллекционер' (Formulas: {formulas_count})")

        # "Тестовый марафонец": 10 тестов за день
        today = datetime.now().date()
        tests_today = Test.query.filter_by(user_id=user_id).filter(Test.date == today).count()
        if tests_today >= 10:
            add_achievement(user_id, "Тестовый марафонец")
            log_info(f"User {user_id} qualifies for 'Тестовый марафонец' (Tests today: {tests_today})")

        # "Недельный стрик": тесты каждый день в течение недели
        week_ago = datetime.now().date() - timedelta(days=6)
        daily_tests = db.session.query(db.func.distinct(db.func.date(Test.date))).filter(
            Test.user_id == user_id,
            Test.date >= week_ago
        ).count()
        if daily_tests >= 7:
            add_achievement(user_id, "Недельный стрик")
            log_info(f"User {user_id} qualifies for 'Недельный стрик' (Daily tests: {daily_tests})")
    except Exception as e:
        log_error(f"Error checking achievements for user {user_id}: {str(e)}")

def add_achievement(user_id, achievement_name):
    try:
        if not Achievement.query.filter_by(user_id=user_id, achievement_name=achievement_name).first():
            new_achievement = Achievement(
                user_id=user_id,
                achievement_name=achievement_name,
                achievement_description=ACHIEVEMENTS[achievement_name]["description"],
                image_path=ACHIEVEMENTS[achievement_name]["image_path"]
            )
            db.session.add(new_achievement)
            db.session.commit()
            log_info(f"Achievement '{achievement_name}' added for user {user_id}")
        else:
            log_debug(f"Achievement '{achievement_name}' already exists for user {user_id}")
    except Exception as e:
        db.session.rollback()
        log_error(f"Failed to add achievement '{achievement_name}' for user {user_id}: {str(e)}")