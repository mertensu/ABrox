from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import datetime
import pprint
from a_process_manager import AProcessManager


class ASettingsWindow(QFrame):
    """Main container for the output settings and run."""
    def __init__(self, internalModel, console, parent=None):
        super(ASettingsWindow, self).__init__(parent)

        self._internalModel = internalModel
        self._console = console
        self._compSettingsFrame = AComputationSettingsFrame(internalModel, console)
        self._modelTestFrame = AModelTestFrame(internalModel, console)

        self._configureLayout(QHBoxLayout())

    def _configureLayout(self, layout):
        """Lays out main components of the frame."""

        self.setFrameStyle(QFrame.Panel)

        layout.addWidget(self._compSettingsFrame)
        layout.addWidget(self._modelTestFrame)
        layout.setStretchFactor(self._compSettingsFrame, 1)
        layout.setStretchFactor(self._modelTestFrame, 2)

        self.setLayout(layout)


class AComputationSettingsFrame(QFrame):
    """Main container for settings and run."""
    def __init__(self, internalModel, console, parent=None):
        super(AComputationSettingsFrame, self).__init__(parent)

        self._internalModel = internalModel
        self._console = console
        self._output = AOuputDir(internalModel)

        self._configureLayout(QVBoxLayout())

    def _configureLayout(self, layout):
        """Lays out main components of the frame."""

        self.setFrameStyle(QFrame.Panel)

        # Create a group box
        groupBox = QGroupBox('Settings')
        groupBoxLayout = QVBoxLayout()

        # Settings entries
        containerLayout = QGridLayout()
        container = QWidget()
        # Define labels
        labels = [('Number of particles:', 'particles'),
                  ('Threshold:', 'threshold'),
                  ('Percentile:', 'percentile')]

        # Add labels and spinboxes to grid
        for idx, label in enumerate(labels):
            labelName = labels[idx][0]
            key = labels[idx][1]
            containerLayout.addWidget(QLabel(labelName, self), idx, 0, 1, 1)
            containerLayout.addWidget(ASettingEntry(self._internalModel, key), idx, 1, 1, 1)

        # Create objective and method choice widgets
        methodChoiceWidget = AMethodChoiceBox(self._internalModel)
        objectiveChoiceWidget = AObjectiveChoiceBox(self._internalModel, methodChoiceWidget)

        containerLayout.addWidget(objectiveChoiceWidget, idx+1, 0, 1, 2)
        containerLayout.addWidget(methodChoiceWidget, idx+2, 0, 1, 2)
        # Lay out container
        container.setLayout(containerLayout)

        groupBoxLayout.addWidget(self._output)
        groupBoxLayout.addWidget(container)
        groupBox.setLayout(groupBoxLayout)
        layout.addWidget(groupBox)
        layout.addStretch(1)
        # Add layout to widget
        self.setLayout(layout)


class ASettingEntry(QDoubleSpinBox):
    """Derives from a basic line edit to include a key, corresponding to the model setting."""

    def __init__(self, internalModel, key, parent=None):
        super(ASettingEntry, self).__init__(parent)

        self._internalModel = internalModel
        self._key = key

        # Adjust spinbox range
        self._configureRange()

        # Set value from model
        self.setValue(self._internalModel['settings'][key])
        self.valueChanged.connect(self._onValueChanged)

    def _configureRange(self):
        """Sets the range of the spinbox."""

        if self._key == 'percentile':
            self.setRange(0.0, 1.0)
            self.setSingleStep(0.1)
        else:
            self.setRange(0.0, 1e10)

    def _onValueChanged(self, val):
        """Triggered when user changes the value fo the setting."""

        self._internalModel.changeSetting(self._key, val)


class AOuputDir(QWidget):
    """Main output dir widget for specifying output location."""
    def __init__(self, internalModel, parent=None):
        super(AOuputDir, self).__init__(parent)

        self._internalModel = internalModel
        self._configureLayout(QHBoxLayout())

    def _configureLayout(self, layout):
        """Creates and sets the layout."""

        # Create edit for path
        self._path = QLineEdit()
        self._path.setPlaceholderText('Output location...')
        self._path.textChanged.connect(self._onEdit)

        # Create edit for dir name (session name)
        self._fileName = QLineEdit()
        self._fileName.setPlaceholderText('Script name...')
        self._fileName.textChanged.connect(self._onName)
        self._fileName.setMaximumSize(self._fileName.sizeHint())

        # Create button for dir
        self._button = QToolButton()
        self._button.setIcon(QIcon('./icons/load.png'))
        self._button.setToolTip('Select output directory...')
        self._button.setStatusTip('Select output directory...')
        self._button.clicked.connect(self._onOpen)

        # Add widgets to layout
        layout.addWidget(self._button)
        layout.addWidget(self._path)
        layout.addWidget(self._fileName)
        layout.setSpacing(0)

        self.setLayout(layout)

    def _onOpen(self):
        """Opens up a file dialog for choosing an output folder."""

        # Create file dialog
        dirPath = QFileDialog.getExistingDirectory(self, 'Select an Empty Output Directory...',
                                                   '', QFileDialog.ShowDirsOnly)

    def _onEdit(self, text):
        """Triggered when user types into dir edit."""

        pass

    def _onName(self, text):
        """Triggered when user types into session edit."""

        pass

    def updateDirName(self, newSession):
        """Called externally to update dir name from model."""

        pass


class AModelTestFrame(QFrame):
    """Main container for the model testing"""
    def __init__(self, internalModel, console, parent=None):
        super(AModelTestFrame, self).__init__(parent)

        self._internalModel = internalModel
        self._console = console
        self._processManager = AProcessManager(self._internalModel, self._console)

        self._configureLayout(QVBoxLayout())

    def _configureLayout(self, layout):
        """Lays out main components of the frame."""

        self.setFrameStyle(QFrame.Panel)

        # Create a group box
        groupBox = QGroupBox('Model Test Settings')
        groupBoxLayout = QVBoxLayout()

        # Create a checkbox
        self._modelTest = QCheckBox()
        self._modelTest.clicked.connect(self._onModelTest)
        self._modelTest.setText('Model Test')

        # Create a combo in its own widget
        self._comboWidget = QWidget()
        comboWidgetLayout = QHBoxLayout()
        comboWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self._combo = AModelComboBox(self._internalModel)
        self._combo.setCurrentText('Pick a Model')
        self._combo.installEventFilter(self)
        configButton = self._createButton('Set Parameter', './icons/config',
                                          self._onSetParameter, Qt.NoFocus, True)
        comboWidgetLayout.addWidget(self._combo)
        comboWidgetLayout.addWidget(configButton)
        comboWidgetLayout.setStretchFactor(self._combo, 5)
        comboWidgetLayout.setStretchFactor(configButton, 1)
        self._comboWidget.setLayout(comboWidgetLayout)
        self._comboWidget.setEnabled(False)

        # Create run abd stop
        self._run = self._createButton('Run', './icons/run', self._onRun,
                                       Qt.NoFocus, True)
        self._stop = self._createButton('Stop', './icons/stop', self._onStop,
                                        Qt.NoFocus, False)
        # Create progress bar
        self._progress = QProgressBar()
        self._progress.setOrientation(Qt.Horizontal)

        buttonsWidget = QWidget()
        buttonsWidgetLayout = QHBoxLayout()
        buttonsWidgetLayout.setContentsMargins(0, 0, 0, 0)
        buttonsWidgetLayout.addWidget(self._run)
        buttonsWidgetLayout.addWidget(self._stop)
        buttonsWidgetLayout.addWidget(self._progress)
        buttonsWidget.setLayout(buttonsWidgetLayout)

        groupBoxLayout.addWidget(self._modelTest)
        groupBoxLayout.addWidget(self._comboWidget)
        groupBoxLayout.addWidget(buttonsWidget)

        groupBox.setLayout(groupBoxLayout)
        layout.addWidget(groupBox)
        layout.addStretch(1)
        self.setLayout(layout)

    def eventFilter(self, qobject, event):

        if type(qobject) is AModelComboBox:
            if event.type() == QEvent.MouseButtonPress:
                self._combo.clear()
                self._combo.addItems([model.name for model in self._internalModel['models']])
        return False

    def _createButton(self, label, iconPath, func, focusPolicy, enabled):
        """Utility to save typing"""

        button = QPushButton(label)
        button.setIcon(QIcon(iconPath))
        button.clicked.connect(func)
        button.setFocusPolicy(focusPolicy)
        button.setEnabled(enabled)
        return button

    def _onModelTest(self, checked):
        """Controls the appearance of the model test frame."""

        if checked:
            self._comboWidget.setEnabled(True)
        else:
            self._comboWidget.setEnabled(False)

    def _onRun(self):
        """For debugging."""

        HARDCODED_FILE_NAME = "test_script.py"
        scriptCreator = AScriptCreator(self._internalModel)
        scriptCreator.createScript(HARDCODED_FILE_NAME)
        #
        # self._processManager.startAbc(HARDCODED_FILE_NAME)

    def _onStop(self):
        """Kill python thread and subprocess inside."""

        self._processManager.stopAll()

    def _onSetParameter(self):
        pass


class AModelComboBox(QComboBox):
    """Represent a dynamically changing combobox."""
    def __init__(self, internalModel, parent=None):
        super(AModelComboBox, self).__init__(parent)

        self._internalModel = internalModel


class AObjectiveChoiceBox(QWidget):
    def __init__(self, internalModel, methodChoiceWidget, parent=None):
        super(AObjectiveChoiceBox, self).__init__(parent)

        self._internalModel = internalModel
        self._methodChoiceWidget = methodChoiceWidget
        self._configureLayout(QHBoxLayout())

    def _configureLayout(self, layout):
        """Lays out the main components."""

        # Create an exclusive checkbox group
        self.checkGroup = QButtonGroup()
        self.checkGroup.setExclusive(True)
        firstCheck = ACheckBox('inference')
        firstCheck.setText('Inference')
        secondCheck = ACheckBox('comparison')
        secondCheck.setText('Comparison')
        secondCheck.setChecked(True)
        self.checkGroup.addButton(firstCheck)
        self.checkGroup.addButton(secondCheck)
        self.checkGroup.buttonClicked.connect(self._onToggle)

        layout.addWidget(QLabel('Objective:'))
        layout.addWidget(firstCheck)
        layout.addWidget(secondCheck)
        layout.addStretch(3)

        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def _onToggle(self, check):
        """Activated when pne of the buttons in the group toggled."""

        self._internalModel.addObjective(check.value)

        # Control appearance of method checkbox
        if check.value == 'inference':
            self._methodChoiceWidget.setEnabled(False)
        else:
            self._methodChoiceWidget.setEnabled(True)


class AMethodChoiceBox(QWidget):
    def __init__(self, internalModel, parent=None):
        super(AMethodChoiceBox, self).__init__(parent)

        self._internalModel = internalModel
        self._configureLayout(QHBoxLayout())

        if self._internalModel.objective() == "comparison":
            self.setEnabled(False)
        else:
            self.setEnabled(True)

    def _configureLayout(self, layout):
        """Lays out the main components."""

        # Create an exclusive checkbox group
        self.checkGroup = QButtonGroup()
        self.checkGroup.setExclusive(True)
        firstCheck = ACheckBox('rejection')
        firstCheck.setText('Rejection')
        secondCheck = ACheckBox('logistic')
        secondCheck.setText('Logistic')
        secondCheck.setChecked(True)
        self.checkGroup.addButton(firstCheck)
        self.checkGroup.addButton(secondCheck)
        self.checkGroup.buttonClicked.connect(self._onToggle)

        layout.addWidget(QLabel('Method:'))
        layout.addWidget(firstCheck)
        layout.addWidget(secondCheck)
        layout.addStretch(3)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def _onToggle(self, check):
        """Activated when pne of the buttons in the group toggled."""

        self._internalModel.addMethod(check.value)


class ACheckBox(QCheckBox):
    def __init__(self, value, parent=None):
        super(ACheckBox, self).__init__(parent)

        self.value = value


class AScriptCreator:
    """
    Handles the creation of a runnable python script. Accepts the gui model
    as first parameter and uses its interface to get the information needed.
    fileName is the name of the python file to-be-created.
    """

    def __init__(self, internalModel):

        self._internalModel = internalModel

    def createScript(self, fileName):
        """Creates an abs runnable script with the specified fileName."""

        # Get a dictionary of modelName: sim function code
        simulateDict = self._internalModel.simulate()

        # Get project dict and remove project name, since
        # config file does not need a project name
        projectDict = self._internalModel.toDict()
        projectDict = {k: v for value in projectDict.values()
                       for k, v in value.items()}

        # Open file and write components
        with open(fileName, 'w') as outfile:
            self._writeHeader(outfile)
            self._writeImports(outfile)
            self._writeSummaryAndDistFunc(outfile)
            self._writeSimulateFuncs(outfile, simulateDict)
            self._writeConfig(outfile, projectDict, simulateDict)
            self._writeAlgorithmCall(outfile)

    def _writeHeader(self, outfile):
        """Write header with info and date."""

        header = '"""\n' \
                 'This is an automatically generated script by ABrox GUI.\n' \
                 'Created on {}.\n' \
                 '"""\n\n'.format(datetime.datetime.now())
        outfile.write(header)

    def _writeImports(self, outfile):
        """Write imports needed for abc."""

        imports = '# Required imports\n' \
                  'import numpy as np\n' \
                  'from scipy import stats\n' \
                  'from abrox.core.algorithm import Abc\n\n\n'

        outfile.write(imports)

    def _writeSummaryAndDistFunc(self, outfile):
        """Write summary and distance (if specified) code."""

        # Write summary
        outfile.write(self._internalModel.summary())
        outfile.write('\n\n\n')

        # Write distance
        if self._internalModel.distance() is not None:
            outfile.write(self._internalModel.distance())
            outfile.write('\n\n\n')

    def _writeSimulateFuncs(self, outfile, simulateDict):
        """Write simulate functions code."""

        for key in simulateDict:
            # The value of simulateDict is a 2-tuple (0 - code, 1 - name)
            outfile.write(simulateDict[key][0])
            outfile.write('\n\n\n')

    def _writeConfig(self, outfile, projectDict, simulateDict):
            """Creates the config file in a nice format. Pretty nasty."""

            # Write var name
            outfile.write('CONFIG = {\n')
            # Write data file
            outfile.write('{}"data": {{\n'.format(self.tab()))
            outfile.write('{}"datafile": "{}"\n'.format(self.tab(2),
                                                        projectDict['data']['datafile']))
            outfile.write('{}}},\n'.format(self.tab()))

            # Write models
            outfile.write('{}"models": [\n'.format(self.tab()))
            for model in projectDict['models']:
                outfile.write('{}{{\n'.format(self.tab(2)))
                outfile.write('{}"name": "{}",\n'.format(self.tab(2),
                                                         model['name']))
                # Write priors
                outfile.write('{}"priors": [\n'.format(self.tab(2)))
                for prior in model['priors']:
                    outfile.write('{}{{"{}": {}}},\n'.format(self.tab(3),
                                                             list(prior.keys())[0],
                                                             list(prior.values())[0]))
                # Close priors list
                outfile.write('{}],\n'.format(self.tab(2)))

                # Write simulate
                outfile.write('{}"simulate": {}\n'.format(self.tab(2),
                                                          simulateDict[model['name']][1]))
                # Close this model dict
                outfile.write('{}}},\n'.format(self.tab(2)))
            # Close models list
            outfile.write('{}],\n'.format(self.tab()))

            # Write summary
            outfile.write('{}"summary": summary,\n'.format(self.tab()))

            # Write distance
            outfile.write('{}"distance": {},\n'.format(self.tab(),
                                                       'distance' if projectDict['settings']
                                                       ['distance_metric'] == 'custom' else None))

            # Write settings
            outfile.write('{}"settings": {{\n'.format(self.tab()))
            # Format settings dict using pprint
            settings = pprint.pformat(projectDict['settings']) \
                .replace('{', "") \
                .replace("}", "")
            # Indent output of pprint with 8 spaces
            settings = ''.join(['{}{}'.format(self.tab(2), l) for l in settings.splitlines(True)
                                                              if "outputdir" not in l])
            outfile.write(settings)
            # Close settings dict
            outfile.write('\n{}}}\n'.format(self.tab()))
            # Close config dict
            outfile.write('}\n\n\n')

    def _writeAlgorithmCall(self, outfile):
        """Writes the algorithm call enclosed in an if __name__ == ..."""

        call = 'if __name__ == "__main__":\n' \
               '{}# Create and run an Abc instance\n' \
               '{}abc = Abc(config=CONFIG)\n' \
               '{}abc.run()\n'.format(self.tab(), self.tab(), self.tab())

        outfile.write(call)

    def tab(self, s=1):
        """Returns a string containing 4*s whitespaces."""

        return " " * (s*4)



















