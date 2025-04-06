class UserServiceRouter:

    app_labels = {'user_service', 'auth', 'contenttypes', 'sessions', 'admin'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.app_labels:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.app_labels:
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (obj1._meta.app_label in self.app_labels and
                obj2._meta.app_label in self.app_labels):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'default' and app_label in self.app_labels:
            return True
        if db != 'default' and app_label in self.app_labels:
            return False
        return None


class ProductServiceRouter:

    app_label = 'product_service'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'product_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'product_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (obj1._meta.app_label == self.app_label and
                obj2._meta.app_label == self.app_label):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'product_db' and app_label == self.app_label:
            return True
        if db != 'product_db' and app_label == self.app_label:
            return False
        return None


class OrderServiceRouter:

    app_label = 'order_service'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'order_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'order_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (obj1._meta.app_label == self.app_label and
                obj2._meta.app_label == self.app_label):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'order_db' and app_label == self.app_label:
            return True
        if db != 'order_db' and app_label == self.app_label:
            return False
        return None


class PaymentServiceRouter:

    app_label = 'payment_service'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'payment_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'payment_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (obj1._meta.app_label == self.app_label and
                obj2._meta.app_label == self.app_label):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'payment_db' and app_label == self.app_label:
            return True
        if db != 'payment_db' and app_label == self.app_label:
            return False
        return None


class ShippingServiceRouter:

    app_label = 'shipping_service'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'shipping_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'shipping_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (obj1._meta.app_label == self.app_label and
                obj2._meta.app_label == self.app_label):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'shipping_db' and app_label == self.app_label:
            return True
        if db != 'shipping_db' and app_label == self.app_label:
            return False
        return None


class RecommendationServiceRouter:

    app_label = 'recommendation_service'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'recommendation_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'recommendation_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (obj1._meta.app_label == self.app_label and
                obj2._meta.app_label == self.app_label):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'recommendation_db' and app_label == self.app_label:
            return True
        if db != 'recommendation_db' and app_label == self.app_label:
            return False
        return None


class AnalyticServiceRouter:

    app_label = 'analytic_service'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'analytic_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'analytic_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (obj1._meta.app_label == self.app_label and
                obj2._meta.app_label == self.app_label):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'analytic_db' and app_label == self.app_label:
            return True
        if db != 'analytic_db' and app_label == self.app_label:
            return False
        return None


class AdminServiceRouter:

    app_label = 'admin_service'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'admin_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'admin_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (obj1._meta.app_label == self.app_label and
                obj2._meta.app_label == self.app_label):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'admin_db' and app_label == self.app_label:
            return True
        if db != 'admin_db' and app_label == self.app_label:
            return False
        return None