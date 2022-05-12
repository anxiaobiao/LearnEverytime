# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 16:06:34 2022

@author: Vada
"""
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
from sklearn.model_selection import KFold, cross_val_score

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import RobustScaler

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, StackingClassifier
from sklearn import svm
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import RandomizedSearchCV

# import inspect
# def retrieve_name(var):
#     callers_local_vars = inspect.currentframe().f_back.f_locals.items()
#     return [var_name for var_name, var_val in callers_local_vars if var_val is var]

def rmsle_cv(model, train_x, train_y):
    kf = KFold(shuffle=True, random_state=42).get_n_splits(train_x.values)  # K折交叉验证
    rmse = cross_val_score(model, train_x.values, train_y, scoring="accuracy", cv = kf)
    return(rmse)

def start(train_x, train_y):
    
    # # 逻辑回归
    LR = make_pipeline(RobustScaler(), LogisticRegression())   # 归一化有帮助
    # score = rmsle_cv(LR, train_x, train_y)
    # print("\n逻辑回归的正确率（方差）: {:.4f}%({:.4f})\n".format(score.mean() * 100, score.std()))
    
    # # 随机森林
    RFC = make_pipeline(RobustScaler(), RandomForestClassifier())
    # RFC = RandomForestClassifier()
    # score = rmsle_cv(RFC, train_x, train_y)
    # print("\n随机森林的正确率（方差）: {:.4f}%({:.4f})\n".format(score.mean() * 100, score.std()))
    
    # # SVM
    SVC = make_pipeline(RobustScaler(), svm.SVC())
    # # SVC = svm.SVC()
    # score = rmsle_cv(SVC, train_x, train_y)
    # print("\nSVM的正确率（方差）: {:.4f}%({:.4f})\n".format(score.mean() * 100, score.std()))
    
    # # AdaBoost
    # # AdaBoost = make_pipeline(RobustScaler(), AdaBoostClassifier())
    # AdaBoost = AdaBoostClassifier()
    # score = rmsle_cv(AdaBoost, train_x, train_y)
    # print("\nAdaBoost的正确率（方差）: {:.4f}%({:.4f})\n".format(score.mean() * 100, score.std()))
    
    
    # xgboost
    # xgboost = make_pipeline(RobustScaler(), XGBClassifier())
    xgboost = XGBClassifier()  
    score = rmsle_cv(xgboost, train_x, train_y)
    print("\nxgboost的正确率（方差）: {:.4f}%({:.4f})\n".format(score.mean() * 100, score.std()))
        
    # # MLP神经网络
    mlp = MLPClassifier(solver='lbfgs',activation='logistic')
    # score = rmsle_cv(mlp, train_x, train_y)
    # print("\nMLP的正确率（方差）: {:.4f}%({:.4f})\n".format(score.mean() * 100, score.std()))
    
    level0 = [('SVC', SVC), ('RFC', RFC), ('MLP', mlp)]
    level1 = LR
    stacked_models = StackingClassifier(estimators=level0, final_estimator=level1, cv=5)
    score = rmsle_cv(stacked_models, train_x, train_y)
    print("\n堆叠的正确率（方差）: {:.4f}%({:.4f})\n".format(score.mean() * 100, score.std()))
    
    return stacked_models
    
if __name__ == '__main__':
    
    train = pd.read_csv('../clean/train.csv', index_col=0)
        
    train_y = train.Transported
    train_x = train.drop('Transported', axis=1)
    
    # 开始训练
    models = start(train_x, train_y)
    
    test = pd.read_csv('../clean/test.csv', index_col=0)
    
    answer = pd.read_csv('../data/sample_submission.csv', index_col=0)
    models.fit(train_x, train_y)
    ans = models.predict(test)
    answer.Transported = ans
    answer['Transported'] = answer['Transported'].astype(bool)
    answer.to_csv("stacked_submission.csv")
    
    
    # names = ['LR', 'RFC', 'SVC', 'AdaBoost', 'xgboost', 'mlp']
    
    # for i in range(len(models)):
        
    #     answer = pd.read_csv('../data/sample_submission.csv', index_col=0)
        
    #     models[i].fit(train_x, train_y)
    #     ans = models[i].predict(test)
    #     # ans = pd.DataFrame(ans)
        
    #     answer.Transported = ans
        
    #     # name = retrieve_name(model)[0]
    #     name = names[i]
        
    #     answer.to_csv("{}_submission.csv".format(name))
    
    