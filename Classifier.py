import pickle
import warnings



class Classifier:

    def load_model(self, path):
        file = open(path, 'rb')
        model = pickle.load(file)
        file.close()
        return model

    def __init__(self) -> None:
        self.lda = self.load_model("models\LDA_model")
        self.qda = self.load_model("models\QDA_model")
        self.rf = self.load_model("models\RF_model")
        self.knn = self.load_model("models\KNN_model")
        self.xgb = self.load_model("models\XGB_model")


    def predict(self,model, sample):
        if model == 'lda':
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return int(self.lda.predict(sample.reshape(1, -1))[0])
        elif model == 'qda':
            return int(self.qda.predict(sample.reshape(1, -1))[0])
        elif model == 'rf':
            return int(self.rf.predict(sample.reshape(1, -1))[0])
        elif model == 'knn':
            return int(self.knn.predict(sample.reshape(1, -1))[0])
        elif model == 'xgb':
            return int(self.xgb.predict(sample.reshape(1, -1))[0]) + 1