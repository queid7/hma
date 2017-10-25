import sys
import ys_util as yu


def perm(items, n=None):
    if n is None:
        n = len(items)
    for i in range(len(items)):
        v = items[i:i + 1]
        if n == 1:
            yield v
        else:
            rest = items[:i] + items[i + 1:]
            for p in perm(rest, n - 1):
                yield v + p


def comb(items, n=None):
    if n is None:
        n = len(items)
    for i in range(len(items)):
        v = items[i:i + 1]
        if n == 1:
            yield v
        else:
            rest = items[i + 1:]
            for c in comb(rest, n - 1):
                yield v + c


def makeNumberOfCasesSet(trial_num, possible_values):
    _set = [None] * (len(possible_values) ** trial_num)

    #   count = 0
    #   for pv_1 in possibleValues:
    #       for pv_2 in possibleValues:
    #           ...
    #           for pv_trialNum in possibleValues:
    #               _set[count] = [pv1, pv2,..., pv_trialNum]
    #               count += 1

    count = 0
    for i_list in yu.mrange([len(possible_values)] * trial_num):
        _set[count] = [possible_values[i_list[j]] for j in range(trial_num)]
        count += 1

    return _set


# def makeNumberOfCasesSetFromCasesSets(casesSets):
#    lenList = [None]*len(casesSets)
#    lenSet = 1
#    for i in range(len(casesSets)):
#        lenList[i] = len(casesSets[i])
#        lenSet *= len(casesSets[i])
#    set = [None]*lenSet
#
#    count = 0
#    for i_list in pe.mrange(lenList):
#        set[count] = [casesSets[j][i_list[j]] for j in range(len(i_list))]
#        count += 1
#
#    return set

def countNumberOfCasesSetFromCasesSets(cases_sets):
    lenList = [None] * len(cases_sets)
    lenSet = 1
    for i in range(len(cases_sets)):
        lenList[i] = len(cases_sets[i])
        lenSet *= len(cases_sets[i])
    return lenSet


def makeNumberOfCasesSetFromCasesSets(cases_sets):
    lenList = [None] * len(cases_sets)
    for i in range(len(cases_sets)):
        lenList[i] = len(cases_sets[i])

    for i_list in yu.mrange(lenList):
        yield [cases_sets[j][i_list[j]] for j in range(len(i_list))]


def addNumberOfCasesSets(set1, set2):
    _set = [None] * (len(set1) * len(set2))
    count = 0
    for case1 in set1:
        for case2 in set2:
            _set[count] = [case1, case2]
            count += 1
    return _set


if __name__ == "__main__":

    def test_byMakingParamSet():
        print('test_byMakingParamSet()')
        widthVaules = [5]
        heightValues = [-1, 1]
        numWidthJoints = 1
        numHeightJoints = 6
        numCenters = 2
        widthSet = makeNumberOfCasesSet(numWidthJoints, widthVaules)
        print('widthSet', len(widthSet))
        heightSet = makeNumberOfCasesSet(numHeightJoints, heightValues)
        print('heightSet', len(heightSet))
        paramSetsForOneCenter = addNumberOfCasesSets(widthSet, heightSet)
        print('paramSetsForOneCenter', len(paramSetsForOneCenter))
        paramSets = makeNumberOfCasesSet(numCenters, paramSetsForOneCenter)
        print('paramSets', len(paramSets))


    #        for paramSet in paramSets:
    #            print paramSet

    def test_makeNumberOfCasesSetFromCasesSets():
        set1 = [1, -1]
        set2 = [2, -2]
        set3 = [3, -3]
        _set = [set1, set2, set3]
        print(_set)

        resultSet = makeNumberOfCasesSetFromCasesSets(_set)
        print(countNumberOfCasesSetFromCasesSets(_set))
        print(resultSet)
        for _set in resultSet:
            print(_set)

    test_makeNumberOfCasesSetFromCasesSets()
