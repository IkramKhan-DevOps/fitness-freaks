from src.core.mixins import CoreListViewMixin, CoreDetailViewMixin, CoreCreateViewMixin, CoreUpdateViewMixin, \
    CoreDeleteViewMixin


class FinanceListViewMixin(CoreListViewMixin):
    permission_prefix = 'finance'


class FinanceDetailViewMixin(CoreDetailViewMixin):
    permission_prefix = 'finance'


class FinanceCreateViewMixin(CoreCreateViewMixin):
    permission_prefix = 'finance'


class FinanceUpdateViewMixin(CoreUpdateViewMixin):
    permission_prefix = 'finance'


class FinanceDeleteViewMixin(CoreDeleteViewMixin):
    permission_prefix = 'finance'

