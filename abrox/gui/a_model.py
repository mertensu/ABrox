from PyQt5.QtWidgets import QMessageBox
import copy
import re
import os
from collections import OrderedDict


class AInternalModel:
    """This class represents the internal model for an approximate bayesian estimation."""
    def __init__(self):

        # Create an analysis skeleton as a dict
        self._project = OrderedDict([
            ('Analysis',
                OrderedDict([
                    ('data', {'datafile': None,
                              'delimiter': None}),
                    ('models', [
                        AModel('Model1'),
                    ]),
                    ('summary', ""),
                    ('distance', ""),
                    ('settings', {
                        'outputdir': "",
                        'distance_metric': "default",
                        'simulations': 1000,
                        'threshold': -1,
                        'percentile': 0.05,
                        'objective': 'comparison',
                        'method': 'logistic',
                        'modeltest': False,
                        'fixedparameters': OrderedDict()
                    }
                    )
                    ]
                )
             )
            ]
        )

    def deleteModel(self, nameToRemove):
        """Interface function to remove a model."""

        for idx, model in enumerate(self._project['Analysis']['models']):
            if model.name == nameToRemove:
                self._project['Analysis']['models'].pop(idx)

    def renameModel(self, oldName, newName):
        """Interface function to rename a model."""

        for model in self._project['Analysis']['models']:
            if model.name == oldName:
                model.name = newName

    def addModel(self, name, simulate=None):
        """Interface function to add a new model."""

        model = AModel(name, simulate)
        self._project['Analysis']['models'].append(model)
        return model

    def addPriorToModel(self, paramName, sciPyCode, modelName):
        """Interface function to add a prior name:func to a given model's priors list."""

        for model in self._project['Analysis']['models']:
            if model.name == modelName:
                # add priors returns T or F according to whether added ot not
                return model.addPrior(paramName, sciPyCode)

    def addSimulateToModel(self, simulateCode, modelName):
        """Interface function to add a prior name:func to a given model's priors list."""

        for model in self._project['Analysis']['models']:
            if model.name == modelName:
                model.simulate = simulateCode

    def addSummary(self, summaryCode):
        self._project['Analysis']['summary'] = summaryCode

    def addDistance(self, distanceCode):
        self._project['Analysis']['distance'] = distanceCode

    def addObjective(self, objective):
        self._project['Analysis']['settings']['objective'] = objective

    def addMethod(self, method):
        self._project['Analysis']['settings']['method'] = method

    def addDataFileAndDelimiter(self, datafile, delim):

        self._project['Analysis']['data']['datafile'] = datafile
        self._project['Analysis']['data']['delimiter'] = delim

    def addOutputDir(self, dirPath):
        self._project['Analysis']['settings']['outputdir'] = dirPath

    def addModelIndexForTest(self, idx):
        self._project['Analysis']['settings']['modeltest'] = idx

    def addFixedParameters(self, listOfTuples):

        self._project['Analysis']['settings']['fixedparameters'] = OrderedDict(listOfTuples)

    def selectedModelForTest(self):

        # Make sure a model is selected
        if self._project['Analysis']['settings']['modeltest'] is False or \
                                                              not self.selectedModelIndexValid():
            raise IndexError('No valid model selected for test!')
        idx = self._project['Analysis']['settings']['modeltest']
        return self._project['Analysis']['models'][idx]

    def selectedModelIndexValid(self):
        return False if self._project['Analysis']['settings']['modeltest'] < 0 else True

    def dataFile(self):
        return self._project['Analysis']['data']['datafile']

    def dataFileAndDelimiter(self):

        return self._project['Analysis']['data']['datafile'], \
               self._project['Analysis']['data']['delimiter']

    def modelTest(self):

        return self._project['Analysis']['settings']['modeltest']

    def summary(self):
        """Returns the summary function code as a string."""

        return self._project['Analysis']['summary']

    def distance(self):
        """Returns the summary function code as a string."""

        if self._project['Analysis']['settings']['distance_metric'] == "default":
            return None
        else:
            return self._project['Analysis']['distance']

    def simulate(self):
        """Returns a dict with key-model name functions."""

        # Use this pattern to extract a function name
        pattern = r'(?<=def)(.*)(?=\()'

        simulateCodes = dict()
        for model in self._project['Analysis']['models']:
            # Get function name
            funcName = re.search(pattern, "def simulate():")
            funcName = funcName.group(1).strip()
            # Replace function name
            simulateCode = model.simulate.replace(funcName, funcName + '_' + model.name)
            simulateCodes[model.name] = (simulateCode, funcName + '_' + model.name)
        return simulateCodes

    def objective(self):
        return self._project['Analysis']['settings']['objective']

    def method(self):
        return self._project['Analysis']['settings']['method']

    def outputDir(self):
        return self._project['Analysis']['settings']['outputdir']

    def models(self):
        """Returns the model list."""

        return self._project['Analysis']['models']

    def fixedParameters(self):
        return self._project['Analysis']['settings']['fixedparameters']

    def fileWithPathName(self):
        """
        Checks if directory exists, if exists, changes name so it matches.
        Assumes model has been checked for sanity!
        """

        if os.path.isdir(self._project['Analysis']['settings']['outputdir']):
            return self._fileWithPathName(os.path.join(self._project['Analysis']['settings']['outputdir'],
                                                       'analysis.py'))

    def _fileWithPathName(self, pathToFile):
        """A recursive helper method to not overwrite analysis files."""

        if not os.path.exists(pathToFile):
            return pathToFile
        else:
            # Replace file name with a new one (_1 attached)
            return self._fileWithPathName(pathToFile.replace('.py', '_1.py'))

    def deletePriorFromModel(self, idx, modelName):
        """Interface function to delete a prior fom a given model's priors list."""

        for model in self._project['Analysis']['models']:
            if model.name == modelName:
                model.removePrior(idx)

    def clearData(self):
        self._project['Analysis']['data'] = {'datafile': None,
                                             'delimiter': None}

    def changeSetting(self, key, val):
        self._project['Analysis']['settings'][key] = val

    def setting(self, key):
        return self._project['Analysis']['settings'][key]

    def toDict(self):
        """Returns a dict representation of the entire session."""

        # Make a deep copy fo the project
        projectCopy = copy.deepcopy(self._project)

        # Turn model objects into dicts
        projectCopy['Analysis']['models'] = []
        for model in self._project['Analysis']['models']:
            projectCopy['Analysis']['models'].append(model.toDict())
        return projectCopy

    def overwrite(self, newProject):
        """Overwrites project data member with new project, also creates models."""

        # Create a copy of the project
        self._project = copy.deepcopy(newProject)

        # Create models from the model dicts and add them to the list of models
        newModels = [AModel.fromDict(model) for model in self._project['Analysis']['models']]
        self._project['Analysis']['models'] = newModels

    def sanityCheckPassed(self, parent=None):
        """
        Checks whether model fields of current project are correct.
        Returns True if ok, False otherwise + displays a message explaining
        the problem.
        """

        # ===== Initialize message box ===== #
        msg = QMessageBox()
        errorTitle = 'Could not start an ABC process...'

        # ===== Check if any models specified ===== #
        if not self._project['Analysis']['models']:

            text = 'No models defined. Your project should contain at least one model.'
            msg.critical(parent, errorTitle, text)
            return False

        # ===== Check if data loaded when not doing a model test ===== #
        if self._project['Analysis']['settings']['modeltest'] is False and \
           not self._project['Analysis']['data']['datafile']:

            text = 'Since you are not performing a model test, ' \
                   'you a need to load a data file.'
            msg.critical(parent, errorTitle, text)
            return False

        # ===== Check if output dir specified ===== #
        if not self._project['Analysis']['settings']['outputdir']:
            text = 'No output dir in settings specified!'
            msg.critical(parent, errorTitle, text)
            return False

        # ===== Check if comparison AND models < 1 ===== #
        if self._project['Analysis']['settings']['objective'] == 'comparison' and \
            len(self._project['Analysis']['models']) < 2:

            text = 'You need at least two models for objective "comparison".'
            msg.critical(parent, errorTitle, text)
            return False

        # All checks passed, start process from caller
        return True

    def __iter__(self):
        """Make iteration possible."""

        return iter(self._project['Analysis'])

    def __getitem__(self, key):
        return self._project['Analysis'][key]


class AModel:
    """
    This class represents an individual 
    statistical model amenable to ABrox analysis.
    """

    @classmethod
    def fromDict(cls, modelDict):

        model = cls(modelDict['name'], modelDict['simulate'])
        model._priors = modelDict['priors']
        return model

    def __init__(self, name, simulate=None):

        self.name = name
        self.simulate = simulate
        self._priors = []

    def removePrior(self, idx):
        """Interface to remove a prior."""

        self._priors.pop(idx)

    def addPrior(self, priorName, sciPyCode):
        """Insert a prior (dict with name and function code."""

        # Check if name taken
        for prior in self._priors:
            if list(prior.keys())[0] == priorName:
                return False
        # Name not taken, append
        self._priors.append({priorName: sciPyCode})
        return True

    def hasPriors(self):
        return any(self._priors)

    def toDict(self):
        """Returns an ordered dict representation of itself."""

        return OrderedDict([('name', self.name),
                            ('priors', self._priors),
                            ('simulate', self.simulate)])

    def __repr__(self):

        return 'AModel [Name: {}, Priors: {}'.format(self.name, self._priors)

    def __iter__(self):
        """Make iteration possible."""

        return iter(self._priors)

