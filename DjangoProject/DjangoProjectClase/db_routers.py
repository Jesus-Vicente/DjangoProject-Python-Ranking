# Example of what your router should look like
class MongoRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'rankingInazuma':
            return 'mongodb'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'rankingInazuma':
            return 'mongodb'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'rankingInazuma':
            return db == 'mongodb'
        return None