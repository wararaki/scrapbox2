import abc

class BaseRecommender:
    @abc.abstractmethod
    def fit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def estimate(self):
        raise NotImplementedError
