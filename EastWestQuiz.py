#!/usr/bin/env python3

# East Coast vs West Coast Quiz Using PyQt
# Max Messenger Bouricius
# June 2017
# Quiz that determines whether a user would would be more suited to live on the East Coast or the West Coast based 
# on their responses to a number of personality questions.
# Tools: Python 3 and PyQt5 for GUI creation and interaction.

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from random import shuffle, randint
from operator import itemgetter
import sys
import os
import csv

class App(QApplication):
    """Main application.

       Input: command line arguments <list> (currently none implemented)
       Output: none
    """
    def __init__(self):
        # Initialize parent widget, set app name, create main window, show main window
        QApplication.__init__(self, sys.argv)
        self.setApplicationName("East Coast vs. West Coast Quiz")
        self.mainWindow = MainWindow()
        self.setWindowIcon(QIcon("mainIcon.jpeg"))
        self.mainWindow.show()

class MainWindow(QMainWindow):
    """Main window for application; contains main widget."""
    def __init__(self):
        # Initialize parent widget, initialize window title, create main widget object, set main widget as central widget of main window
        QMainWindow.__init__(self)
        self.setWindowTitle("Quiz App")
        self.mainWidget = MainWidget()
        self.setCentralWidget(self.mainWidget)

        # Author text label to be shown in status bar
        self.testWidget2 = QLabel(" Max Messenger Bouricius 2017 ", alignment = Qt.AlignRight)

        # Initialize progress bar, also in status bar
        self.progressBar = QProgressBar()
        self.progressBar.setMaximum(len(self.mainWidget.questionsArray))
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(self.mainWidget.initialProgress)
        self.progressString = '%v/%m questions answered (%p%)'
        self.progressBar.setFormat(self.progressString)
        self.progressBar.setTextVisible(True)
        self.progressBar.setFixedHeight(15)

        # Initialize menu bar and associated menus
        self.menuBar = QMenuBar(self)
        self.toolBar = QToolBar(self)

        self.fileMenu = QMenu("&File")
        self.helpMenu = QMenu("&Help")

        # Initialize actions for menus: exit, save progress, load progress, open questionnaire, about page, reset quiz
        self.exitAction = QAction(self)
        self.exitAction.setIcon(QIcon("application-exit.png"))
        self.exitAction.setText("&Exit")
        self.exitAction.setShortcut('Ctrl+Q')

        self.saveAction = QAction(self)
        self.saveAction.setIcon(QIcon("document-save.png"))
        self.saveAction.setText("&Save Progress...")
        self.saveAction.setShortcut('Ctrl+S')

        self.loadAction = QAction(self)
        self.loadAction.setIcon(QIcon("document-open.png"))
        self.loadAction.setText("&Open Session...")
        self.loadAction.setShortcut('Ctrl+O')

        self.openQuizAction = QAction(self)
        self.openQuizAction.setIcon(QIcon("document-import.png"))
        self.openQuizAction.setText("&Load Questionnaire...")
        self.openQuizAction.setShortcut('Ctrl+L')

        self.aboutAction = QAction(self)
        self.aboutAction.setIcon(QIcon("help-about.png"))
        self.aboutAction.setText("&About")
        self.aboutAction.setShortcut('F1')

        self.resetAction = QAction(self)
        self.resetAction.setIcon(QIcon("view-refresh.png"))
        self.resetAction.setText("&Restart")
        self.resetAction.setShortcut('Ctrl+R')

        # Populate menubar with menus + actions
        self.fileMenu.addAction(self.loadAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.openQuizAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.resetAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)

        self.helpMenu.addAction(self.aboutAction)

        self.menuBar.addMenu(self.fileMenu)
        self.menuBar.addMenu(self.helpMenu)

        # Populate toolbar with actions
        self.toolBar.addAction(self.loadAction)
        self.toolBar.addAction(self.saveAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.openQuizAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.resetAction)

        # Add menu bar and toolbar to main window
        self.setMenuBar(self.menuBar)
        self.addToolBar(self.toolBar)

        # Connect mainWidget slots to various signals
        self.mainWidget.signalIncrementWidget.connect(self.incrementProgress)
        self.mainWidget.signalSetProgress.connect(self.setProgress)
        self.mainWidget.signalResetWidget.connect(self.progressBar.setValue)
        self.mainWidget.stackedBottom.widget(0).submitButton.clicked.connect(self.mainWidget.tallyResults)
        self.mainWidget.stackedBottom.widget(1).buttonExit.clicked.connect(self.close)
        self.mainWidget.stackedBottom.widget(2).buttonExit.clicked.connect(self.close)
        self.mainWidget.signalUpdateProgressMax.connect(self.setProgressMax)
        self.exitAction.triggered.connect(self.close)
        self.aboutAction.triggered.connect(self.openAboutBox)
        self.saveAction.triggered.connect(self.mainWidget.saveProgress)
        self.loadAction.triggered.connect(self.mainWidget.loadProgress)
        self.resetAction.triggered.connect(self.askReset)
        self.openQuizAction.triggered.connect(self.mainWidget.loadQuestionnaireBox)

        # Add progress bar and name to status bar
        self.statusBar().insertPermanentWidget(0, self.progressBar, stretch = 10)
        self.statusBar().insertPermanentWidget(1, self.testWidget2, stretch = 0)

    def incrementProgress(self):
        """Increments progress bar by one question; connected to MainWidget.signalIncrementWidget."""
        self.progressBar.setValue(self.progressBar.value() + 1)

    def setProgress(self, progress):
        """Sets progress bar to a specific value. Used for saved/loaded progress.

           Input: progress to set bar to <int>
           Output: none
        """
        self.progressBar.setValue(progress)

    def setProgressMax(self, maximum):
        """Sets the progress bar's maximum value for when switching between questionnaires of different lengths.

           Input: maximum value <int>
           Output: none
        """
        self.progressBar.setMaximum(maximum)

    def askExit(self):
        """Prompts the user with a confirmation dialog when they take action to exit the application.

            Input: none
            Output: whether or not to exit <int bool>
        """
        # Open dialog box
        exitDialog = ExitDialog()
        response = exitDialog.exec_()
        if (response == QDialog.Accepted):
            return 1
        else:
            return 0

    def askReset(self):
        """Prompts the user with a confirmation dialog when they take action to restart their quiz.

            Input: none
            Output: none
        """
        # If the user has answered at least one question, ask them to confirm their choice
        if (self.progressBar.value() != 0):
            resetDialog = ResetDialog()
            response = resetDialog.exec_()
            # If they confirm, reset
            if (response == QDialog.Accepted):
                self.mainWidget.resetQuestionButtons()
            # Else, do nothing and resume quiz
            else:
                return 0
        # If no questions have been answered, create popup box telling user there is nothing to reset
        else:
            self.mainWidget.popupBox("Nothing to reset; no questions have been answered yet.")

    def closeEvent(self, event):
        """Override the default close event actions. In this
           case, open a quit dialog instead of directly closing.

           Input:  event <QCloseEvent>
           Output: None
        """
        response = self.askExit()
        if (response == 0):
            event.ignore()
        else:
            QMainWindow.closeEvent(self, event)

    def openAboutBox(self):
        """Creates and displays an 'About' box with program and author information."""
        # Main initializations
        self.aboutBox = QDialog(None, Qt.SplashScreen)
        self.aboutBox.setWindowTitle("About")
        self.mainLayout = QVBoxLayout()
        self.marginLayout = QHBoxLayout()
        self.fullWidget = QWidget()

        # Initialize widgets/layouts for mainLayout
        self.titleLayout1 = QHBoxLayout()
        self.titleLayout2 = QVBoxLayout()
        self.titleLabel = QLabel("Quiz App")
        self.subtitleLabel = QLabel("Max Messenger Bouricius 2017")

        # Initialize help icon picture + size
        self.helpIconPic = QPixmap(os.getcwd() + "/help-about.png")
        self.helpIconPicLabel = QLabel()
        self.iconScale = 1
        self.iconSize = QSize()
        self.iconSize.setWidth(self.helpIconPic.width() * self.iconScale)
        self.iconSize.setHeight(self.helpIconPic.height() * self.iconScale)
        self.helpIconPic = self.helpIconPic.scaled(self.iconSize)
        self.helpIconPicLabel.setPixmap(self.helpIconPic)
        self.hFrame1 = QFrame()

        # Initialize "About the App" section
        self.aboutAppTitle = QLabel("        About the App")
        self.aboutAppLabel = QLabel("       Simple program that loads various questionnaires, asking users some questions about themselves to determine their personal results (e.g. whether they are an East Coast person or a West Coast person, a dog person or a cat person, etc). Some basic research on these topics has allowed these quizzes to be at least somewhat accurate, especially given that my only resources were my (very limited) personal anecdotes and the opinions of strangers on the internet. Tools used were Python 3 and PyQt 5.")
        self.aboutAppLabel.setWordWrap(True)
        self.hFrame2 = QFrame()

        # Initialize "About the Author" section
        self.aboutAuthorTitle = QLabel("        About the Author")
        self.authorLayout = QHBoxLayout()

        # Initialize headshot picture + size
        self.aboutAuthorPic = QPixmap(os.getcwd() + "/img/authorPhoto.jpg")
        self.aboutAuthorPicLabel = QLabel()
        self.picScale = 0.5
        self.picSize = QSize()
        self.picSize.setWidth(self.aboutAuthorPic.width() * self.picScale)
        self.picSize.setHeight(self.aboutAuthorPic.height() * self.picScale)
        self.picStyle = """QFrame{
            border: 2px solid gray;
            border-radius: 5px;
            }"""
        self.aboutAuthorPic = self.aboutAuthorPic.scaled(self.picSize)
        self.aboutAuthorPicLabel.setPixmap(self.aboutAuthorPic)
        self.aboutAuthorPicLabel.setStyleSheet(self.picStyle)

        self.aboutAuthorLabel = QLabel("    My last name is pronounced 'Messenger Bur-REE-shis', for all those who were wondering. I am a student, computer geek, and musician at heart; when I am not sitting behind a computer or drowning in schoolwork, I am composing music for a local video game company or arranging songs for my a cappella group and for a cappella groups across the front range. Find me on Github (github.com/gerlacus) and Soundcloud (soundcloud.com/gerlacus).")
        self.aboutAuthorLabel.setWordWrap(True)

        self.okButton = QPushButton("OK")

        self.authorLayout.addSpacing(8)
        self.authorLayout.addWidget(self.aboutAuthorPicLabel)
        self.authorLayout.addSpacing(12)
        self.authorLayout.addWidget(self.aboutAuthorLabel)

        # Initialize fonts
        self.mainTitleFont = QFont()
        self.mainTitleFont.setPixelSize(36)
        self.mainTitleFont.setBold(True)

        self.subtitleFont = QFont()
        self.subtitleFont.setPixelSize(24)
        self.subtitleFont.setItalic(True)

        self.secondaryTitleFont = QFont()
        self.secondaryTitleFont.setPixelSize(12)
        self.secondaryTitleFont.setBold(True)

        # Set fonts accordingly
        self.titleLabel.setFont(self.mainTitleFont)
        self.subtitleLabel.setFont(self.subtitleFont)
        self.aboutAppTitle.setFont(self.secondaryTitleFont)
        self.aboutAuthorTitle.setFont(self.secondaryTitleFont)

        # Set frame styles
        self.hFrame1.setFrameStyle(QFrame.HLine)
        self.hFrame2.setFrameStyle(QFrame.HLine)

        self.hFrame1.setFrameShadow(QFrame.Sunken)
        self.hFrame2.setFrameShadow(QFrame.Sunken)

        # Populate layouts
        self.titleLayout2.addWidget(self.titleLabel, alignment = Qt.AlignLeft)
        self.titleLayout2.addWidget(self.subtitleLabel, alignment = Qt.AlignLeft)
        self.titleLayout1.addStretch(20)
        self.titleLayout1.addWidget(self.helpIconPicLabel)
        self.titleLayout1.addSpacing(20)
        self.titleLayout1.addLayout(self.titleLayout2)
        self.titleLayout1.addSpacing(40)

        self.mainLayout.addSpacing(4)
        self.mainLayout.addLayout(self.titleLayout1)
        self.mainLayout.addSpacing(8)
        self.mainLayout.addWidget(self.hFrame1)
        self.mainLayout.addSpacing(4)
        self.mainLayout.addWidget(self.aboutAppTitle)
        self.mainLayout.addWidget(self.aboutAppLabel)
        self.mainLayout.addSpacing(6)
        self.mainLayout.addWidget(self.hFrame2)
        self.mainLayout.addWidget(self.aboutAuthorTitle)
        self.mainLayout.addSpacing(4)
        self.mainLayout.addLayout(self.authorLayout)
        self.mainLayout.addSpacing(0)
        self.mainLayout.addWidget(self.okButton, alignment = Qt.AlignRight)

        self.marginLayout.addSpacing(20)
        self.marginLayout.addLayout(self.mainLayout)
        self.marginLayout.addSpacing(20)

        # Set fixed size for whole dialog box
        self.sizeFixed = QSize()
        self.sizeFixed.setWidth(590)
        self.sizeFixed.setHeight(470)
        self.aboutBox.setFixedSize(self.sizeFixed)
        self.aboutBox.setLayout(self.marginLayout)

        # Apply stylesheet to entire dialog
        self.boxStyle = """QDialog{
            border: 1px solid gray;
            border-radius: 5px;
            }"""
        self.aboutBox.setStyleSheet(self.boxStyle)

        # Connect "OK" button to "accept"
        self.okButton.clicked.connect(self.aboutBox.accept)

        # Display about box
        self.aboutBox.exec_()

class ResetDialog(QDialog):
    """Creates and displays a 'Reset?' dialog prompting user to confirm that they want to reset the quiz."""
    def __init__(self):
        # Parent initialization
        QDialog.__init__(self, flags=Qt.SplashScreen)

        # Initialize layouts + widgets
        self.mainLayout = QVBoxLayout(self)
        self.secondaryLayout = QHBoxLayout()

        self.titleText = QLabel("Are you sure you want to restart?")
        self.dialogText = QLabel("Any unsaved progress will be lost.")

        self.cancelButton = QPushButton("Cancel")
        self.quitButton = QPushButton("Restart")

        # Connect buttons
        self.cancelButton.clicked.connect(self.reject)
        self.quitButton.clicked.connect(self.accept)

        # Initialize hLine frame
        self.hLine = QFrame()
        self.hLine.setFrameShape(QFrame.HLine)
        self.hLine.setFrameShadow(QFrame.Sunken)
        
        # Add title font, apply font to title label
        self.titleFont = QFont()
        self.titleFont.setBold(True)
        self.titleText.setFont(self.titleFont)

        # Populate layouts
        self.secondaryLayout.addWidget(self.cancelButton)
        self.secondaryLayout.addWidget(self.quitButton)
        
        self.mainLayout.addWidget(self.titleText, alignment = Qt.AlignCenter)
        self.mainLayout.addWidget(self.hLine)
        self.mainLayout.addWidget(self.dialogText, alignment = Qt.AlignCenter)
        self.mainLayout.addSpacing(4)
        self.mainLayout.addLayout(self.secondaryLayout)

        # Customize appearance
        self.setFixedSize(self.sizeHint())
        self.setFixedWidth(275)
        self.boxStyle = """QDialog{
            border: 1px solid gray;
            border-radius: 5px;
            }"""
        self.setStyleSheet(self.boxStyle)

class ExitDialog(QDialog):
    """Creates and displays an 'Exit?' dialog prompting user to confirm that they want to exit the quiz."""
    def __init__(self):
        # Parent initialization
        QDialog.__init__(self, flags=Qt.SplashScreen)

        # Initialize layouts + widgets
        self.mainLayout = QVBoxLayout(self)
        self.secondaryLayout = QHBoxLayout()

        self.titleText = QLabel("Are you sure you want to quit?")
        self.dialogText = QLabel("Any unsaved progress will be lost.")

        self.cancelButton = QPushButton("Cancel")
        self.quitButton = QPushButton("Quit")

        # Connect buttons
        self.cancelButton.clicked.connect(self.reject)
        self.quitButton.clicked.connect(self.accept)

        # Initialize hLine frame
        self.hLine = QFrame()
        self.hLine.setFrameShape(QFrame.HLine)
        self.hLine.setFrameShadow(QFrame.Sunken)
        
        # Add title font, apply font to title label
        self.titleFont = QFont()
        self.titleFont.setBold(True)
        self.titleText.setFont(self.titleFont)

        # Populate layouts
        self.secondaryLayout.addWidget(self.cancelButton)
        self.secondaryLayout.addWidget(self.quitButton)
        
        self.mainLayout.addWidget(self.titleText, alignment = Qt.AlignCenter)
        self.mainLayout.addWidget(self.hLine)
        self.mainLayout.addWidget(self.dialogText, alignment = Qt.AlignCenter)
        self.mainLayout.addSpacing(4)
        self.mainLayout.addLayout(self.secondaryLayout)

        # Customize appearance
        self.setFixedSize(self.sizeHint())
        self.setFixedWidth(275)
        self.boxStyle = """QDialog{
            border: 1px solid gray;
            border-radius: 5px;
            }"""
        self.setStyleSheet(self.boxStyle)

class RadioButtons(QWidget):
    """Container class for each question. Includes question number, question name, 6 radio buttons, and 'Agree ... Disagree' text."""
    # Signal: when question has been answered for the first time, and thus should trigger increment in progress
    signalIncrementButton = pyqtSignal(object)

    def __init__(self, eastWest, questionNum, questionText):
        # Initialize parent widget
        QWidget.__init__(self)

        # Whether an answer will count towards the West tally (0) or East tally (1)
        self.isEast = eastWest
        # Which of the 5 radio buttons are currently selected. Initialized as none (-1)
        self.whichPressed = -1
        # Has the question been answered yet? used for incrementing purposes
        self.isAnswered = 0
        # Absolute ID of the question
        self.absID = 0

        # Initialize radio buttons
        self.button1 = QRadioButton()
        self.button2 = QRadioButton()
        self.button3 = QRadioButton()
        self.button4 = QRadioButton()
        self.button5 = QRadioButton()
        self.button6 = QRadioButton()

        # Initialize bold font for questionNum
        self.boldFont1 = QFont()
        self.boldFont1.setBold(True)

        # Initialize questionLabel and dis/agr labels
        self.questionLabel = QLabel(questionText)
        self.questionLabel.setWordWrap(False)
        self.disLabel = QLabel("Disagree")
        self.agrLabel = QLabel("Agree")

        # Initialize separate question number on side
        self.questNum = questionNum
        self.questNumFormat = str(questionNum) + "."
        self.questNumLabel = QLabel(self.questNumFormat)
        self.questNumLabel.setFont(self.boldFont1)
        self.questNumLabel.setMargin(0)
        self.questNumLabel.setScaledContents(False)

        # Initialize layouts and groups
        self.questionLayout = QHBoxLayout()
        self.buttonsLayout = QHBoxLayout()
        self.disAgrLayout= QHBoxLayout()
        self.mainLayout = QVBoxLayout()
        self.mainLayout2 = QVBoxLayout(self)
        self.mainGroup = QGroupBox()
        self.mainWidget = QWidget()

        # Populate questionLayout with labels
        self.questionLayout.addWidget(self.questNumLabel, alignment=Qt.AlignLeft)
        self.questionLayout.addSpacing(0)
        self.questionLayout.addStretch(1)
        self.questionLayout.addWidget(self.questionLabel)
        self.questionLayout.addStretch(1)

        # Connect button signals to slots (buttons 1-6)
        self.button1.clicked.connect(self.getWhichButtonPressed)    # button 1
        self.button1.clicked.connect(self.shouldProgressIncrement)
        self.button2.clicked.connect(self.getWhichButtonPressed)    # button 2
        self.button2.clicked.connect(self.shouldProgressIncrement)
        self.button3.clicked.connect(self.getWhichButtonPressed)    # button 3
        self.button3.clicked.connect(self.shouldProgressIncrement)
        self.button4.clicked.connect(self.getWhichButtonPressed)    # button 4
        self.button4.clicked.connect(self.shouldProgressIncrement)
        self.button5.clicked.connect(self.getWhichButtonPressed)    # button 5
        self.button5.clicked.connect(self.shouldProgressIncrement)
        self.button6.clicked.connect(self.getWhichButtonPressed)    # button 6
        self.button6.clicked.connect(self.shouldProgressIncrement)

        # Populate buttonsLayout with buttons (1-6)
        self.buttonsLayout.addStretch(5)
        self.buttonsLayout.addWidget(self.button1)
        self.buttonsLayout.addStretch(10)
        self.buttonsLayout.addWidget(self.button2)
        self.buttonsLayout.addStretch(10)
        self.buttonsLayout.addWidget(self.button3)
        self.buttonsLayout.addStretch(10)
        self.buttonsLayout.addWidget(self.button4)
        self.buttonsLayout.addStretch(10)
        self.buttonsLayout.addWidget(self.button5)
        self.buttonsLayout.addStretch(10)
        self.buttonsLayout.addWidget(self.button6)
        self.buttonsLayout.addStretch(5)

        # Populate disAgrLayout with dis/agr labels
        self.disAgrLayout.addStretch(2)
        self.disAgrLayout.addWidget(self.disLabel)
        self.disAgrLayout.addStretch(20)
        self.disAgrLayout.addWidget(self.agrLabel)
        self.disAgrLayout.addStretch(2)

        # Add all layouts to group
        self.mainLayout.addStretch(10)
        self.mainLayout.addLayout(self.questionLayout)
        self.mainLayout.addStretch(5)
        self.mainLayout.addLayout(self.buttonsLayout)
        self.mainLayout.addStretch(5)
        self.mainLayout.addLayout(self.disAgrLayout)
        self.mainLayout.addStretch(10)
        self.mainGroup.setLayout(self.mainLayout)
        self.mainLayout2.addWidget(self.mainGroup)
        self.setLayout(self.mainLayout2)

        # Customize appearance: initialize + apply stylesheet for group
        self.styleSheet = (""" QGroupBox{
                border: 1px solid gray;
                border-radius: 4px;
                background-color: rgb(70, 70, 70);
                } """)
        self.mainGroup.setStyleSheet(self.styleSheet)
        self.mainGroup.setFlat(True)

    def signalIncrementFromRadioButtons(self):
        """Emits signal for mainWidget to relay required info to mainWindow to increment progress bar."""
        self.signalIncrementButton.emit()

    def getCoast(self):
        """Returns which coast the question refers to (e.g. which final result 'agreeing' to this question will promote).
           0 = West coast, 1 = East coast.
        """
        return self.isEast

    def getWhichButtonPressed(self):
        """Returns which button, if any, is currently selected.

           Input: none
           Output: which button is pressed <int> in range 0-5 (or -1, if no button is pressed)
        """
        if (self.button1.isChecked()):
            self.whichPressed = 0
            return 0
        elif (self.button2.isChecked()):
            self.whichPressed = 1
            return 1
        elif (self.button3.isChecked()):
            self.whichPressed = 2
            return 2
        elif (self.button4.isChecked()):
            self.whichPressed = 3
            return 3
        elif (self.button5.isChecked()):
            self.whichPressed = 4
            return 4
        elif (self.button6.isChecked()):
            self.whichPressed = 5
            return 5
        else:
            return -1

    def getQuestNum(self):
        """Returns, out of all questions, which question this one is.
        
           Input: none
           Output: question number <int>
        """
        return self.questNum

    def shouldProgressIncrement(self):
        """If question has not been answered, then set it to 'answered' and send the signal to increment progress.
           Otherwise, do nothing; question has already been answered and the user is merely changing their response.
           Triggered by clicked signal on any button.

           Input: none
           Output: none
        """
        if (self.isAnswered == 0):
            # Increment detected; mark question as answered and send signal to increment window
            self.isAnswered = 1
            self.signalIncrementButton.emit(1)

    def resetButtons(self):
        """Resets all 6 buttons in the question to unchecked state and marks question as 'unanswered'."""
        self.button1.setAutoExclusive(False)
        self.button1.setChecked(False)
        self.button1.setAutoExclusive(True)

        self.button2.setAutoExclusive(False)
        self.button2.setChecked(False)
        self.button2.setAutoExclusive(True)

        self.button3.setAutoExclusive(False)
        self.button3.setChecked(False)
        self.button3.setAutoExclusive(True)

        self.button4.setAutoExclusive(False)
        self.button4.setChecked(False)
        self.button4.setAutoExclusive(True)

        self.button5.setAutoExclusive(False)
        self.button5.setChecked(False)
        self.button5.setAutoExclusive(True)

        self.button6.setAutoExclusive(False)
        self.button6.setChecked(False)
        self.button6.setAutoExclusive(True)

        # Mark question as no longer answered
        self.isAnswered = 0

class FullBottomLayoutStack(QStackedLayout):
    """Stacked layout at bottom of quiz. Layout indeces are as follows:
        0: initial "submit my answers" button.
        1: "west coast" results page, if the user's answers resulted in a "west coast" conclusion.
        2: "east coast" results page, if the user's answers resulted in an "east coast" conclusion.
    """
    def __init__(self, resultsTitles, resultsTexts, resultsPics):
        # Initialize parent widget
        QStackedLayout.__init__(self)

        # Initialize pre-results layouts
        self.submitLayout = PreResultsLayout()

        # Initialize widgets, associate each with layout
        self.submitWidget = PreResultsLayout()
        self.westWidget = ResultsLayout(0, resultsTitles, resultsTexts, resultsPics)
        self.eastWidget = ResultsLayout(1, resultsTitles, resultsTexts, resultsPics)

        # Add layouts to self
        self.addWidget(self.submitWidget)
        self.addWidget(self.westWidget)
        self.addWidget(self.eastWidget)
       
        # Initialize index to "submit"
        self.setCurrentIndex(0)

    def updateInfo(self, resultsTitles, resultsTexts, resultsPics):
        """Updates results title and description text of each results when user loads in new file.

           Input: questionnaire ID <int>
           Output: None
        """
        self.westWidget.updateResultsInfo(resultsTitles, resultsTexts, resultsPics)
        self.eastWidget.updateResultsInfo(resultsTitles, resultsTexts, resultsPics)


class TitleLayout(QWidget):
    """Title info at top of window (quiz title and header text)."""
    def __init__(self, title, questionnaireID):
        # Initialize parent widget
        QWidget.__init__(self)

        # Change title text depending on which questionnaire has been loaded
        self.questionnaireIndex = questionnaireID

        # Widgets contained in QVBoxLayout
        self.mainLayout = QVBoxLayout(self)

        # Initialize titleText based on argument "title"
        self.titleText = QLabel(title)
        self.descriptText = QLabel("Take this quiz to find out!")

        # Initialize title font, assign said font to titleText label
        self.titleFont = QFont()
        self.titleFont.setBold(True)
        self.titleFont.setPixelSize(24)
        self.titleText.setFont(self.titleFont)
        self.titleText.setWordWrap(False)

        # Initialize description font, assign said font to descriptText
        self.descriptFont = QFont()
        self.descriptFont.setBold(False)
        self.descriptFont.setPixelSize(16)
        self.descriptText.setFont(self.descriptFont)

        # Add widgets to full layout
        self.mainLayout.addWidget(self.titleText, alignment=Qt.AlignCenter)
        self.mainLayout.addSpacing(0)
        self.mainLayout.addWidget(self.descriptText, alignment=Qt.AlignCenter)

    def updateTitle(self, quizTitle):
        """Updates the quiz title in the event of loading a new questionnaire

           Input: quizTitle []
           Output: none
        """
        self.titleText.setText(quizTitle)


class PreResultsLayout(QWidget):
    """Layout with 'Submit' button, shown before user has completed quiz. First of three layouts in stacked bottom layout."""
    def __init__(self):
        # Initialize parent widget
        QWidget.__init__(self)
        # Based on QHBoxLayout, though could feasibly be a QVBoxLayout too
        self.layout = QHBoxLayout()

        # Initialize submit button
        self.submitButton = QPushButton("Submit My Answers!")
        self.submitButton.setMinimumWidth(350)
        self.submitButton.setMinimumHeight(100)

        # Initialize font for button, assign said font to button
        self.buttonFont = QFont()
        self.buttonFont.setPixelSize(36)
        self.submitButton.setFont(self.buttonFont)

        # Add button to layout, set primary widget's layout
        self.layout.addStretch(10)
        self.layout.addWidget(self.submitButton)
        self.layout.addStretch(10)
        self.setLayout(self.layout)

class ResultsLayout(QWidget):
    """'Results' layout, shown after user has completed quiz and obtained a result.
        Initialized with bool pertaining to whether results are for option 0 (originally 'West coast') or option 1 (originally 'East coast').
        Both are initialized and created upon startup, but only the relevant layout is made visible in the end.
    """
    def __init__(self, pageID, resultsTitles, resultsTexts, resultsPics):
        # Initialize parent widget
        QWidget.__init__(self)
        
        # Initialize layouts + widgets
        self.pageID = pageID
        self.layout = QVBoxLayout()                     # Overarching layout
        self.title = QLabel()                           # Title
        self.primaryLayout = QHBoxLayout()              # Primary layout
        self.picScale = 0.4                             # Size of scaled image; 1 = no scaling
        self.descriptionText = QLabel()                 # Description label
        self.descriptionText.setWordWrap(True)
        self.buttonsLayout = QHBoxLayout()              # Layout for "retake" + "exit" buttons
        self.buttonRetake = QPushButton("Retake Quiz")  # "Retake" button
        self.buttonExit = QPushButton("Exit")           # "Exit" button
        self.picture = QLabel()                         # Picture to accompany description
        self.hLine1 = QFrame()

        # Customize horizontal frame
        self.hLine1.setFrameStyle(QFrame.HLine)
        self.hLine1.setFrameShadow(QFrame.Sunken)

        # Font for title (bold, 24px)
        self.titleFont = QFont()                        
        self.titleFont.setBold(True)
        self.titleFont.setPixelSize(24)
        self.title.setFont(self.titleFont)              # Assign said font to title

        # Font for button labels
        self.buttonFont = QFont()
        self.buttonFont.setPixelSize(16)

        # Set title/text to whichever questionnaire has been chosen
        self.title.setText(resultsTitles[pageID])
        self.descriptionText.setText(resultsTexts[pageID])

        # If pageID = 0, initialize as "West coast"
        if (pageID == 0):
            self.picPixMap = QPixmap(resultsPics[0])
        # Else pageID = 1, so initialize as "East coast"
        else:
            self.picPixMap = QPixmap(resultsPics[1])
        
        # Use QSize to scale picture accordingly
        self.testSize = QSize()
        self.testSize.setWidth(self.picPixMap.width() * self.picScale)
        self.testSize.setHeight(self.picPixMap.height() * self.picScale)
        self.picPixMap = self.picPixMap.scaled(self.testSize)

        # Stylesheet for picture border to match main theme of question boxes
        self.picStyle = """QFrame{
            border: 2px solid gray;
            border-radius: 5px;
            }"""
        self.picture.setPixmap(self.picPixMap)
        self.picture.setScaledContents(False)
        self.picture.setStyleSheet(self.picStyle)

        # Populate title layout
        self.layout.addWidget(self.title, alignment=Qt.AlignCenter)     # Title label
        self.layout.addSpacing(10)

        # Populate primary layout
        self.primaryLayout.addStretch(20)
        self.primaryLayout.addSpacing(20)
        self.primaryLayout.addWidget(self.picture)                      # Picture
        self.primaryLayout.addSpacing(20)
        self.primaryLayout.addWidget(self.descriptionText)              # Description label
        self.primaryLayout.addSpacing(20)
        self.primaryLayout.addStretch(20)

        # Customize buttons -- min width and font
        self.buttonRetake.setMinimumWidth(200)                          # "Retake" button
        self.buttonRetake.setFont(self.buttonFont)
        self.buttonExit.setMinimumWidth(200)                            # "Exit" button
        self.buttonExit.setFont(self.buttonFont)

        # Buttons layout -- "retake" + "exit"
        self.buttonsLayout.addStretch(8)
        self.buttonsLayout.addWidget(self.buttonRetake)
        self.buttonsLayout.addStretch(2)
        self.buttonsLayout.addSpacing(16)
        self.buttonsLayout.addWidget(self.buttonExit)
        self.buttonsLayout.addStretch(8)

        # Full layout included in widget
        self.layout.addLayout(self.primaryLayout)
        self.layout.addSpacing(16)
        self.layout.addWidget(self.hLine1)
        self.layout.addSpacing(16)
        self.layout.addLayout(self.buttonsLayout)
        self.setLayout(self.layout)


    def updateResultsInfo(self, resultsTitles, resultsTexts, resultsPics):
        """Updates results title and description text when user loads in new file.

           Input: questionnaire ID <int>
           Output: None
        """
        # Set title + description texts to relevant questionnaire
        self.title.setText(resultsTitles[self.pageID])
        self.descriptionText.setText(resultsTexts[self.pageID])

        # Re-initialize picture
        self.picPixMap = QPixmap(resultsPics[self.pageID])
        self.picture.setPixmap(self.picPixMap)
        self.testSize = QSize()
        self.testSize.setWidth(self.picPixMap.width() * self.picScale)
        self.testSize.setHeight(self.picPixMap.height() * self.picScale)
        self.picPixMap = self.picPixMap.scaled(self.testSize)

        # Stylesheet for picture border to match main theme of question boxes
        self.picStyle = """QFrame{
            border: 2px solid gray;
            border-radius: 5px;
            }"""
        self.picture.setPixmap(self.picPixMap)
        self.picture.setScaledContents(False)
        self.picture.setStyleSheet(self.picStyle)


class questionnairesArray(object):
    """Class of arrays to contain all questionnaire information.
        Included information: questions, titles, shortened titles, descriptions, results titles, results text, results pictures paths.
    """
    def __init__(self):
        # Actual questions
        self.questions = []
        # Titles for quizzes
        self.titles = []
        # Shortened quiz titles (for questionnaireBox)
        self.shortTitles = []
        # Descriptions for quizzes
        self.descriptions = []
        # Titles for quiz results
        self.resultsTitles = []
        # Text for quiz results
        self.resultsText = []
        # Picture directories for quiz results
        self.resultsPicsDirs = []

        # QUIZ 1: East Coast vs West Coast
        self.questions.append([["Overall, I prefer cold rain over snow.", 0, -1, 0],
                ["I would rather spend the day hiking in the forest than shopping downtown.", 0, -1, 1],
                ["I would rather have more leisure time than work extra hours at my job to finish a project early.", 0, -1, 2],
                ["In the summer, I prefer to wear flip flops over boat shoes.", 0, -1, 3],
                ["My ideal career would be in a tech-related field.", 0, -1, 4],
                ["I care deeply about recycling and composting.", 0, -1, 5],
                ["I prefer to go to parties that start and end earlier in the night rather than later.", 0, -1, 6],
                ["I like to drink cheap, local, and readily-available wine over more expensive and exotic brands.", 0, -1, 7],
                ["I don't mind driving for an hour or two to get to the next big city nearest to my own.", 0, -1, 8],
                ["I prefer fast-paced, urban energy to a more relaxed lifestyle.", 1, -1, 9],
                ["A wide selection of local beers is not all that important to me.", 1, -1, 10],
                ["My idea of fashion prioritizes layering over accessorizing.", 1, -1, 11],
                ["Living near urban centers with lots of entertainment/shopping opportunities is important to me.", 1, -1, 12],
                ["I am not very affected by bad weather.", 1, -1, 13],
                ["I get irritated when people are walking too slowly in front of me and I have somewhere to be.", 1, -1, 14],
                ["I think it is more important to be truthful than to avoid hurting someone's feelings.", 1, -1, 15],
                ["In the winter, I would rather wear a nice pea coat than a flannel jacket.", 1, -1, 16],
                ["I like the idea of dressing in a sophisticated and professional manner for my job.", 1, -1, 17]])
        self.titles.append("Are You More Suited for the East\n   Coast or for the West Coast?")
        self.shortTitles.append("East Coast vs West Coast")
        self.descriptions.append("Would you prefer a life on the East Coast, or are you more suited for living on the West Coast? Answer a few questions about your lifestyle and this quiz will tell you which coast you truly belong on.")
        self.resultsTitles.append(["Results: You Belong on the West Coast!", "Results: You Belong on the East Coast!"])
        self.resultsText.append(["Duuude, you're definitely a West Coaster. You probably like hoodies and don't feel the need to dress up for work. You hate the snow, but you're fine with rain (ESPECIALLY if you like Portland or Seattle). You love outdoorsy activities like camping, hiking, and surfing. You believe that personal well-being, caring about the environment, and connecting with others are the most important things in life. You know what they say: West Coast best coast!", "You're an East Coaster at heart. You walk fast, talk fast, and don't put up with any BS. You like the idea of big cities being within feasible driving distance, and you can put up with cold weather just fine. You feel that big cities like New York and Boston have so much history and culture to them that you can't help but want to live on the East Coast. You're probably reading this in your pea coat on your way to work. You know what they say: work hard, play hard!"])
        self.resultsPicsDirs.append([os.getcwd() + "/img/WestCoastEDIT.jpg", os.getcwd() + "/img/EastCoastEDIT.jpg"])

        # QUIZ 2: Cat Person versus Dog Person
        self.questions.append([["I was exposed to cats frequently as a child.", 0, -1, 0],
                ["Dogs were a common pet in my childhood.", 1, -1, 1],
                ["A night spent at home watching Netflix sounds more appealing than a night on the town.", 0, -1, 2],
                ["When I go to the beach, I'd rather play frisbee with friends than watch the sunset alone.", 1, -1, 3],
                ["I consider myself a creative, 'non-traditional' thinker.", 0, -1, 4],
                ["I get anxious if I don't spend enough time outside being active.", 1, -1, 5],
                ["I don't like playing by the rules, especially if the rules are illogical and impede my productivity.", 0, -1, 6],
                ["I prefer group projects over independent work.", 1, -1, 7],
                ["George Harrison was a better Beatle than Paul McCartney.", 0, -1, 8],
                ["I find humor based on clever wordplay to be confusing and/or pretentious.", 1, -1, 9],
                ["I can see myself living in a studio apartment.", 0, -1, 10],
                ["I would enjoy living in a house with many roommates.", 1, -1, 11],
                ["I am sometimes accused of being 'standoffish' or otherwise emotionally distant.", 0, -1, 12],
                ["My viewpoints and beliefs tend to be more conservative than liberal.", 1, -1, 13],
                ["I would rather live in an urban area near a coastline than in a rural area in the middle of the country.", 0, -1, 14],
                ["I tend to live my life in a positive, uplifting mindset.", 1, -1, 15],
                ["I sometimes feel like I worry about certain things more than most people do.", 0, -1, 16],
                ["I am trusting of others, sometimes to a fault.", 1, -1, 17],
                ["I tend to draw my energy from creative pursuits, rather than physical activity.", 0, -1, 18],
                ["I dislike the idea of a long-distance relationship, and I wouldn't want to be in one.", 1, -1, 19]])
        self.titles.append("  Are You More of a Cat\nPerson or a Dog Person?")
        self.shortTitles.append("Cat Person vs Dog Person")
        self.descriptions.append("Feline friends or canine companions? Which one suits you more? Based on a few questions about your personality and habits, this quiz will determine which animal you'd be better off having as a pet.")
        self.resultsTitles.append(["Results: You Are a Cat Person!", "Results: You Are a Dog Person!"])
        self.resultsText.append(["You definitely prefer the company of a feline friend. You're probably a creative soul who'd rather spend a day painting a picture or writing poetry than going out and being social. Not to say that you're not a social being -- just that you're not the kind of person to bounce around a party greeting everybody whether you know them or not. You would probably be fine living in a small apartment in or near a city, so long as you have a cat to sit on your lap in the evening.","You like your canine companions! You're the kind of person who feels energized through being sociable and connecting with a wide variety of friends. Staying inside all day sounds like a nightmare to you; you'd rather get out of the house and do something active, especially with friends! And if it were socially acceptable, you'd probably stick your head out the car window just like a dog. After all, life is a wild ride, and you're here to enjoy every second of it."])
        self.resultsPicsDirs.append([os.getcwd() + "/img/CatPersonEDIT.jpg", os.getcwd() + "/img/DogPersonEDIT.jpg"])

        # QUIZ 3: Wine Person vs Beer Person
        self.questions.append([["I tend to enjoy dressing up and looking sharp for a night out.", 0, -1, 0],
                ["I prefer a more laid-back drinking environment over a more formal tone.", 1, -1, 1],
                ["I am not afraid to spend more money on a more exquisite drink.", 0, -1, 2],
                ["When I buy booze, I tend to buy whatever has the highest alcohol content for the lowest price.", 1, -1, 3],
                ["Most of my social interactions are with a significant other.", 0, -1, 4],
                ["I tend to hang out with groups of friends rather than with individuals one on one.", 1, -1, 5],
                ["I live (or would like to live) on the coast rather than the central area of the country.", 0, -1, 6],
                ["Given the choice, I would rather live in Germany than in France.", 1, -1, 7],
                ["I tend to worry about how many calories I consume in a day.", 0, -1, 8],
                ["I am concerned about my daily sugar intake.", 1, -1, 9],
                ["I prefer to drink alcohol that has been imported from other states or countries.", 0, -1, 10],
                ["I enjoy drinking locally-produced beverages.", 1, -1, 11]])
        self.titles.append("   Are You a Beer Person\n        or a Wine Person?")
        self.shortTitles.append("Beer Person vs Wine Person")
        self.descriptions.append("Do you enjoy the classy nature of wine, or are you more of a laid-back craft brew drinker? Answer a handful of questions and this quiz will determine which booze should be your go-to this weekend.")
        self.resultsTitles.append(["Results: You Are A Wine Person!", "Results: You Are A Beer Person!"])
        self.resultsText.append(["You prefer the finer things in life, and wine is certainly no exception. A refined drink for refined tastes, you enjoy the dignified nature and exotic charm of drinking an imported wine over the rambunctious energy of drinking a beer brewed down the street. Wine is perfect for a night spent at a fancy restaurant with your significant other or simply curling up with each other to watch a movie at home. You couldn't be happier about being a wine person!", "Whether it be lagers, ales, stouts, or any other manner of beer, chances are you prefer it over the more limited selection of wines. You enjoy the idea of drinking what is, at its core, a local product -- in fact, some of the best beer may practically be brewed in your backyard! Most importantly, however, you enjoy the camraderie and social atmosphere of drinking with groups of friends that beer is so apt on cultivating. So crack open a cold one and enjoy!"])
        self.resultsPicsDirs.append([os.getcwd() + "/img/WinePersonEDIT.jpg", os.getcwd() + "/img/BeerPersonEDIT.jpg"])

        """
        # QUIZ 4: Placeholder quiz, to test functionality of dynamically-scaled questionnaire loading dialog
        self.questions.append([["Test question 1", 0, -1, 0],
                ["Test question 2", 1, -1, 1],
                ["Test question 3", 0, -1, 2],
                ["Test question 4", 1, -1, 3]])
        self.titles.append("   Test Title 2?")
        self.shortTitles.append("Test Title 2")
        self.descriptions.append("This is also a test quiz. It's not very fun, but try it out if you'd like. Also, this is a test to see what happens when I type too far into the dialog box. Will it scroll? Will it overflow? Let's find out. Test test test test test test test test test that's ten tests. I think this should be enough text to sufficiently overfill the text edit. Cool. Done. Bye.")
        self.resultsTitles.append(["Results: Answer 0!", "Results: Answer 1!"])
        self.resultsText.append(["You took this meaningless quiz, and got an answer of 0. In a binary world, that means you are false. Neat!", "You took a pointless quiz and got an answer of 1. If this were binary, you'd be true, but that doesn't really mean all that much on its own, does it? Oh well."])
        self.resultsPicsDirs.append(['0', '0'])
        """

    def getSize(self):
        """Returns the number of questionnaires.
           Input: none
           Output: number of questionnaires <int>
        """
        return len(self.questions)

    def getAllShortTitles(self):
        """Returns complete list of short titles of questionnaires.
           Input: none
           Output: list of short titles [<str>]
        """
        return self.shortTitles

    def getQuestions(self, index):
        """Returns the complete list of question text/properties for the given questionnaire.
           Input: questionnaire ID
           Output: questions array [[question text <str>, which answer pertains to <bool/int>, which button is pressed <int>, absolute question number <int>]]
        """
        return self.questions[index]

    def getQuizTitle(self, index):
        """Get title of quiz for given index.
           Input: questionnaire ID
           Output: questionnaire title <str>
        """
        return self.titles[index]

    def getQuizDescription(self, index):
        """Get description of quiz for given index.
           Input: questionnaire ID
           Output: quiz description <str>
        """
        return self.descriptions[index]

    def getResultsTitles(self, index):
        """Get titles for results for quiz of given index.
           Input: questionnaire ID
           Output: results titles [results title 0 <str>, results title 1 <str>]
        """
        return self.resultsTitles[index]

    def getResultsTexts(self, index):
        """Get paragraph descriptions of results for quiz of given index.
           Input: questionnaire ID
           Output: results text [results text 0 <str>, results title 1 <str>]
        """
        return self.resultsText[index]

    def getResultsPics(self, index):
        """Get paths to pictures for quiz results for quiz of given index.
           Input: questionnaire ID
           Output: results picture paths [path 0 <str>, path 1 <str>]
        """
        return self.resultsPicsDirs[index]


class QuestionnairesTable(QTableWidget):
    """Table to hold questionnaire titles; used in questionnaire loading dialog."""
    def __init__(self, shortTitlesArray):
        QTableWidget.__init__(self)

        # Initialized with shortTitles array
        self.shortTitles = shortTitlesArray

        # Customize appearance
        self.setColumnCount(1)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setLineWidth(1)
        self.setFrameShadow(QFrame.Plain)

        # Populate tables with available questionnaires
        self.setRowCount(len(self.shortTitles))
        for i in range(0, self.rowCount()):
            self.setCellWidget(i, 0, QLabel(self.shortTitles[i], alignment = Qt.AlignCenter))

        # Set first element to already be highlighted
        self.setCurrentCell(0, 0)

        # Final appearance customizations (widget dimensions)
        self.setColumnWidth(0, 301)
        self.setFixedHeight(self.rowHeight(0) * self.rowCount() + 2)

class MainWidget(QWidget):
    """Main widget; contains all visible content, including scrollable area/scrollbar."""
    # Custom signals
    signalIncrementWidget = pyqtSignal(object)      # When progressBar progress must be triggered
    signalSetProgress = pyqtSignal(object)          # When progressBar progress must be set to a specific value
    signalChangeStack = pyqtSignal(object)          # Upon sumitting results, change bottom stack to according layout
    signalResetWidget = pyqtSignal(object)          # When user clicks "reset quiz" from either results page
    signalUpdateProgressMax = pyqtSignal(object)    # When user loads a questionnaire of possibly different length than previous questionnaire

    def __init__(self):
        # Initialize parent widget
        QWidget.__init__(self)
        self.loadedProgress = 0                     # 0 signifies initial load. 1 signifies subsequent loads
        self.questionnaires = questionnairesArray() # Load copy of questionnaires within self scope
        self.questionnaireIndex = 0                 # Whichever questionnaire gets loaded in via dialog

        self.isBorn = 0                             # If 0, questionnaireBox will have no cancel button

        self.loadQuestionnaireBox()

        # Assign all questions to dictionary
        # Format: {absID : corresponding array in self.questionsArray}
        self.questionsDict = {}

        # Add questions to dictionary in format described above
        self.populateDictionary()

        # Initialize layouts
        self.mainLayout = QHBoxLayout(self)
        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)                  # Contains all questions
        self.stackedBottom = FullBottomLayoutStack(self.questionnaires.getResultsTitles(self.questionnaireIndex), self.questionnaires.getResultsTexts(self.questionnaireIndex), self.questionnaires.getResultsPics(self.questionnaireIndex))

        # Connect signals to relevant slots
        self.signalChangeStack.connect(self.stackedBottom.setCurrentIndex)                      # Change to results layout based on answers
        self.stackedBottom.widget(1).buttonRetake.clicked.connect(self.resetQuestionButtons)    # Reset questions upon clicking "reset"
        self.stackedBottom.widget(2).buttonRetake.clicked.connect(self.resetQuestionButtons)

        # Initialize scroll area
        self.scrollArea = QScrollArea()
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setWidgetResizable(True)

        # Initialize initial progress tally; used for loaded progress to accurately reflect on progress bar
        self.initialProgress = 0
        self.radioButtonsArray = []

        # Initialize title widget
        self.title = TitleLayout(self.questionnaires.getQuizTitle(self.questionnaireIndex), self.questionnaireIndex)

        # Load the initial quiz based on the id + array + questions dictionary
        self.loadInitialProgress()

        # Add scrollArea to main layout, set min width/height
        self.mainLayout.addWidget(self.scrollArea)
        self.setMinimumWidth(self.scrollWidget.width() + 35)
        self.setMinimumHeight(480)

    def populateDictionary(self):
        """Populates questions dictionary with current array's question contents."""
        self.sortedQuestionsArray = sorted(self.questionsArray, key=itemgetter(3))
        for i in range(0, len(self.sortedQuestionsArray)):
            self.questionsDict[i] = self.sortedQuestionsArray[i]

    def loadInitialProgress(self):
        """The initial call to load questions from the pre-loaded array.

           Input: none
           Output: none
        """

        # If not first load, depopulate whatever's already there
        if (self.loadedProgress == 1):
            # Depopulate all non-radioButton widgets/layouts, too
            self.title.setParent(None)
            self.stackedBottom.setParent(None)
            # Update title widget text + results pics/text
            self.stackedBottom.updateInfo(self.questionnaires.getResultsTitles(self.questionnaireIndex), self.questionnaires.getResultsTexts(self.questionnaireIndex), self.questionnaires.getResultsPics(self.questionnaireIndex))
            self.title.updateTitle(self.questionnaires.getQuizTitle(self.questionnaireIndex))
            # Depopulate existing buttons
            while (self.radioButtonsArray):
                #self.radioButtonsArray[0].whichPressed = -1
                self.radioButtonsArray[0].setParent(None)
                self.radioButtonsArray.pop(0)
                self.hFrame2.setParent(None)
                self.hFrame1.setParent(None)

        # Populate all non-radioButton widgets/layouts
        self.populateButtonsArray(self.questionsArray, self.loadedProgress)

        # Populate main (scroll) layout
        self.scrollLayout.addWidget(self.title)
        self.hFrame1 = QFrame()
        self.hFrame2 = QFrame()
        self.hFrame1.setFrameStyle(QFrame.HLine)
        self.hFrame1.setFrameShadow(QFrame.Sunken)
        self.hFrame2.setFrameStyle(QFrame.HLine)
        self.hFrame2.setFrameShadow(QFrame.Sunken)

        self.scrollLayout.addWidget(self.hFrame1)
        self.scrollLayout.addStretch(10)      
        for x in self.radioButtonsArray:                    # Add radioButtons to layout via loop
            self.scrollLayout.addWidget(x)
            self.scrollLayout.addStretch(10)
        self.scrollLayout.addWidget(self.hFrame2)
        self.scrollLayout.addLayout(self.stackedBottom)
        self.scrollArea.setHorizontalScrollBarPolicy(1)     # 1: Never shown
        self.scrollArea.setVerticalScrollBarPolicy(0)       # 0: Always shown
        self.signalSetProgress.emit(self.initialProgress)

        # Set scroll position back to top of window
        self.scrollArea.verticalScrollBar().setValue(0) 
        self.stackedBottom.setCurrentIndex(0)

    def loadProgress(self):
        """Subsequent calls to load progress (from saved files).

           Input: none
           Output: none
        """
        # If true after file has been inspected, then load method will proceed
        self.isValidFile = False

        # Open dialog, grab wanted array
        self.fileDialog = QFileDialog()
        self.path = self.fileDialog.getOpenFileName(parent=self, filter="Text files (*.txt)", directory = os.getcwd())[0]
        # If user cancels, and thus no path was obtained
        if (self.path == ""):
            return

        # Open file, add to array
        self.shortQuestionsArray = list(csv.reader(open(self.path, 'r'), delimiter=','))
        try:
            int(self.shortQuestionsArray[0][0])
        except:
            self.popupBox("Error: savefile header invalid.")
            return

        if (len(self.shortQuestionsArray[0]) == 1) and (0 <= int(self.shortQuestionsArray[0][0]) < len(self.questionnaires.getAllShortTitles())):
            self.questionnaireIndex = int(self.shortQuestionsArray[0][0])
        else:
            self.popupBox("Error: savefile header invalid or refers to nonexistent questionnaire.")
            return
        
        # Rectify "first element is None" issue
        self.shortQuestionsArray.pop(0)
        
        # Prospective new array being loaded in, before being checked for validity
        self.newQuestionsArray = self.questionnaires.getQuestions(self.questionnaireIndex)

        # Check if new array is of valid format
        if (len(self.shortQuestionsArray) == len(self.newQuestionsArray)):
            # Array to check if each question has exactly 1 recorded response/appearance in save file
            # Initial population of [0, 0, ..., 0]

            self.populatedQuestions = []
            for i in range(0, len(self.shortQuestionsArray)):
                self.populatedQuestions.append(0)

            # Actual inspection of file
            for i in range(0, len(self.shortQuestionsArray)):
                if (len(self.shortQuestionsArray[i]) == 2):
                    # Check to see if both parts of inArray are valid integers
                    try:
                        int(self.shortQuestionsArray[i][1])
                        int(self.shortQuestionsArray[i][0])
                    except:
                        break
                    if (-1 <= int(self.shortQuestionsArray[i][1]) <= 5) and (0 <= int(self.shortQuestionsArray[i][0]) < len(self.newQuestionsArray)):
                        self.populatedQuestions[int(self.shortQuestionsArray[i][0])] += 1
                        self.isValidFile = True
                    else:
                        self.isValidFile = False
                        break

            # Final check to see if all questions were answered exactly once
            for i in range(0, len(self.newQuestionsArray)):
                if (self.populatedQuestions[i] != 1):
                    self.isValidFile = False
                    break

        # If all tests have been passed and file is entirely valid
        if (self.isValidFile):
            self.questionsArray = self.questionnaires.getQuestions(self.questionnaireIndex)
            # Depopulate current layouts
            if (self.loadedProgress == 1):
                # Depopulate all non-radioButton widgets/layouts, too
                self.stackedBottom.setParent(None)
                # Depopulate existing buttons
                while (self.radioButtonsArray):
                    #self.radioButtonsArray[0].whichPressed = -1
                    self.radioButtonsArray[0].setParent(None)
                    self.radioButtonsArray.pop(0)
                    self.hFrame2.setParent(None)
                    self.hFrame1.setParent(None)
            self.questionsArray = self.questionnaires.getQuestions(self.questionnaireIndex)
            # Repopulate with new input
            self.populateButtonsArrayShort(self.shortQuestionsArray, self.loadedProgress)

            # Update title widget text + results pics/text
            self.stackedBottom.updateInfo(self.questionnaires.getResultsTitles(self.questionnaireIndex), self.questionnaires.getResultsTexts(self.questionnaireIndex), self.questionnaires.getResultsPics(self.questionnaireIndex))
            self.title.updateTitle(self.questionnaires.getQuizTitle(self.questionnaireIndex))

            # Populate main (scroll) layout
            self.scrollLayout.addWidget(self.title)

            # Initialize frames (horizontal lines)
            self.hFrame1 = QFrame()
            self.hFrame2 = QFrame()
            self.hFrame1.setFrameStyle(QFrame.HLine)
            self.hFrame1.setFrameShadow(QFrame.Sunken)
            self.hFrame2.setFrameStyle(QFrame.HLine)
            self.hFrame2.setFrameShadow(QFrame.Sunken)

            # Repopulate scrollLayout
            self.scrollLayout.addWidget(self.hFrame1)
            self.scrollLayout.addStretch(10)      
            for x in self.radioButtonsArray:        # Add radioButtons to layout via loop
                self.scrollLayout.addWidget(x)
                self.scrollLayout.addStretch(10)
            self.scrollLayout.addWidget(self.hFrame2)
            self.scrollLayout.addLayout(self.stackedBottom)
            self.scrollArea.setHorizontalScrollBarPolicy(1)  # enum!
            self.scrollArea.setVerticalScrollBarPolicy(0)
            self.signalSetProgress.emit(self.initialProgress)

            self.scrollArea.verticalScrollBar().setValue(0)
            self.stackedBottom.setCurrentIndex(0)
            self.popupBox("Savefile successfully loaded.")
        else:
            self.popupBox("Error: savefile invalid.")

    def populateButtonsArrayShort(self, inArray, loaded):
        """Populates the buttons array given short array (absID, response).

           Input: inArray[[]], whether loading from file or not <bool/int>
           Output: none
        """
        # Initial value to set progress bar to upon finishing creation (begins at 0, increments with every already-answered question)
        self.initialProgress = 0
        self.numQuestions = 18          # 0-17 = 18 questions total

        # Update dictionary, in case of change in quiz
        self.populateDictionary()

        # Iterate through inArray, initializing RadioButtons and setting their questions/recorded responses accordingly
        for i in range(0, len(inArray)):
            inArray[i][0] = int(inArray[i][0])
            inArray[i][1] = int(inArray[i][1])
            # Create RadioButtons class for each question based on information given in questionsArray
            # Format: RadioButtons(eastWest, questionNumber, questionText) 
            self.currentQuestion = self.questionsDict[inArray[i][0]]
            self.radioButtonsArray.append (RadioButtons(self.currentQuestion[1], i+1, self.currentQuestion[0]))
            self.radioButtonsArray[i].signalIncrementButton.connect(self.signalIncrementFromMainWidget)
            self.radioButtonsArray[i].whichPressed = inArray[i][1]

            # If button is already pressed
            if (inArray[i][1] != -1):
                self.initialProgress += 1
                self.radioButtonsArray[i].isAnswered = 1
                # Set button to be pressed
                if (inArray[i][1] == 0):
                    self.radioButtonsArray[i].button1.setChecked(True)
                elif (inArray[i][1] == 1):
                    self.radioButtonsArray[i].button2.setChecked(True)
                elif (inArray[i][1] == 2):
                    self.radioButtonsArray[i].button3.setChecked(True)
                elif (inArray[i][1] == 3):
                    self.radioButtonsArray[i].button4.setChecked(True)
                elif (inArray[i][1] == 4):
                    self.radioButtonsArray[i].button5.setChecked(True)
                else:
                    self.radioButtonsArray[i].button6.setChecked(True)

            self.signalUpdateProgressMax.emit(len(self.questionsArray))

    def populateButtonsArray(self, inArray, loaded):
        """Populates the buttons array.

            argument: inArray[[]], whether_loading_from_file_or_not <int>"""

        # If not loading from file, then shuffle
        if (loaded == 0):
            self.loadedProgress = 1
            shuffle(inArray)

        # Progress that progress bar will ultimately be set to
        self.initialProgress = 0

        for i in range(0, len(inArray)):
            # Cast from string input to int (method only called after confirmation that input can be cast to int)
            inArray[i][1] = int(inArray[i][1])
            inArray[i][2] = int(inArray[i][2])

            # Create RadioButtons class for each question based on information given in questionsArray
            # Format: RadioButtons(eastWest, questionNumber, questionText) 
            self.radioButtonsArray.append (RadioButtons(inArray[i][1], i+1, inArray[i][0]))
            self.radioButtonsArray[i].signalIncrementButton.connect(self.signalIncrementFromMainWidget)
            self.radioButtonsArray[i].whichPressed = inArray[i][2]

            # If button is already pressed
            if (inArray[i][2] != -1):
                self.initialProgress += 1
                self.radioButtonsArray[i].isAnswered = 1
                # Set button to be pressed
                if (inArray[i][2] == 0):
                    self.radioButtonsArray[i].button1.setChecked(True)
                elif (inArray[i][2] == 1):
                    self.radioButtonsArray[i].button2.setChecked(True)
                elif (inArray[i][2] == 2):
                    self.radioButtonsArray[i].button3.setChecked(True)
                elif (inArray[i][2] == 3):
                    self.radioButtonsArray[i].button4.setChecked(True)
                elif (inArray[i][2] == 4):
                    self.radioButtonsArray[i].button5.setChecked(True)
                else:
                    self.radioButtonsArray[i].button6.setChecked(True)

    def signalIncrementFromMainWidget(self):
        """When a RadioButtons class has deemed a click as one that should add to the full progress,
           this signal tells the progress bar in the main window.
        """
        self.signalIncrementWidget.emit(1)

    def loadQuestionnaireBox(self):
        """Startup dialog that prompts user to choose a questionnaire.

           Input: none
           Output: none
        """
        # Initialize widgets/layouts
        self.introDialog = QDialog(None, Qt.SplashScreen)
        self.introDialog.mainLayout = QVBoxLayout()
        self.introDialog.buttonsLayout = QHBoxLayout()
        self.introDialog.mainText = QLabel("FWEF")
        self.introDialog.table = QuestionnairesTable(self.questionnaires.getAllShortTitles())
        self.introDialog.titleText = QLabel("Please Select a Questionnaire")
        self.introDialog.stackedDescriptions = QStackedLayout()
        self.introDialog.hFrame1 = QFrame()
        self.introDialog.hFrame2 = QFrame()
        self.introDialog.OKButton = QPushButton("Take Quiz!")
        self.introDialog.cancelButton = QPushButton("Cancel")

        # Descriptions for stacked layout
        self.introDialog.description0= QTextEdit()
        self.introDialog.description0.setReadOnly(True)
        self.introDialog.description0.setPlaceholderText("Fwef0")
        self.introDialog.description1= QTextEdit()
        self.introDialog.description1.setReadOnly(True)
        self.introDialog.description2= QTextEdit()
        self.introDialog.description2.setReadOnly(True)

        # Initialize fonts, apply to labels
        self.introDialog.titleFont = QFont()
        self.introDialog.titleFont.setBold(True)
        self.introDialog.titleFont.setPixelSize(20)
        self.introDialog.titleText.setFont(self.introDialog.titleFont)

        self.introDialog.tableFont = QFont()                        
        self.introDialog.tableFont.setPixelSize(16)
        self.introDialog.table.setFont(self.introDialog.tableFont)

        # Add to stacked layout programmatically
        for i in range(0, self.questionnaires.getSize()):
            self.introDialog.stackedDescriptions.addWidget(QTextEdit())

        # Use loop to customize stacked descriptions
        for i in range(0, self.introDialog.stackedDescriptions.count()):
            self.introDialog.stackedDescriptions.widget(i).setReadOnly(True)
            self.introDialog.stackedDescriptions.widget(i).setPlaceholderText(self.questionnaires.getQuizDescription(i))
            self.introDialog.stackedDescriptions.widget(i).setFixedHeight(75)

        # Customize frames
        self.introDialog.hFrame1.setFrameShape(QFrame.HLine)
        self.introDialog.hFrame1.setFrameShadow(QFrame.Sunken)

        self.introDialog.hFrame2.setFrameShape(QFrame.HLine)
        self.introDialog.hFrame2.setFrameShadow(QFrame.Sunken)

        # Populate layout(s)
        self.introDialog.mainLayout.addWidget(self.introDialog.titleText, alignment = Qt.AlignCenter)
        self.introDialog.mainLayout.addWidget(self.introDialog.hFrame1)
        self.introDialog.mainLayout.addWidget(self.introDialog.table)
        self.introDialog.mainLayout.addLayout(self.introDialog.stackedDescriptions)

        # If initial load, don't give option to cancel
        if (self.isBorn == 1):
            self.introDialog.buttonsLayout.addWidget(self.introDialog.cancelButton, alignment = Qt.AlignLeft)
            self.introDialog.buttonsLayout.addWidget(self.introDialog.OKButton, alignment = Qt.AlignRight)
            self.introDialog.mainLayout.addLayout(self.introDialog.buttonsLayout)

        else:
            self.isBorn = 1
            self.introDialog.mainLayout.addWidget(self.introDialog.OKButton)

            self.questionnaireIndex = 0

            # Grab questions, shuffle order
            self.questionsArray = self.questionnaires.getQuestions(0)
            shuffle(self.questionsArray)
        
        self.introDialog.setLayout(self.introDialog.mainLayout)

        # Shortcut for enter = self.closeQuestionnaireBox
        self.introDialog.shortcutClose = QShortcut(self.introDialog)
        self.introDialog.shortcutClose.setKey(Qt.Key_Return)

        # Connect signals to slots
        self.introDialog.cancelButton.clicked.connect(self.introDialog.close)
        self.introDialog.OKButton.clicked.connect(self.closeQuestionnaireBox)
        self.introDialog.table.cellDoubleClicked.connect(self.closeQuestionnaireBox)
        self.introDialog.table.currentCellChanged.connect(self.updateQuestionnaireBoxDescription)
        self.introDialog.shortcutClose.activated.connect(self.closeQuestionnaireBox)

        # Set QDialog width to accomodate table
        self.introDialog.setFixedWidth(325)
        self.introDialog.setFixedHeight(180 + self.introDialog.table.rowHeight(0) * self.introDialog.table.rowCount() + 2)

        # Initialize + set style sheet
        self.boxStyle = """QDialog{
            border: 1px solid gray;
            border-radius: 5px;
            }"""
        self.introDialog.setStyleSheet(self.boxStyle)


        self.introDialog.exec_()

    def updateQuestionnaireBoxDescription(self, currentRow):
        """Updates questionnaire box description to whichever quiz is selected, as per signal by user interaction."""
        self.introDialog.stackedDescriptions.setCurrentIndex(currentRow)

    def closeQuestionnaireBox(self):
        """Upon user pressing 'Load Quiz' button on questionnaire box, return which questionnaire was selected and close the box.
           Also reinitializes title, progressBar, and results.

           Input: none
           Output: questionnaire index <int>
        """
        # Set questionnaireIndex to current selected row in questionnaire dialog
        self.questionnaireIndex = self.introDialog.table.currentRow()

        # Grab questions, shuffle order
        self.questionsArray = self.questionnaires.getQuestions(self.questionnaireIndex)
        shuffle(self.questionsArray)

        # If not first time loading
        if (self.loadedProgress == 1):
            self.loadInitialProgress()
            self.stackedBottom.updateInfo(self.questionnaires.getResultsTitles(self.questionnaireIndex), self.questionnaires.getResultsTexts(self.questionnaireIndex), self.questionnaires.getResultsPics(self.questionnaireIndex))
            self.title.updateTitle(self.questionnaires.getQuizTitle(self.questionnaireIndex))
            self.signalUpdateProgressMax.emit(len(self.questionsArray))

        self.introDialog.close()

    def popupBox(self, text):
        """Rudimentary popup box with "OK" button for various notifications/displays of information to user.
           In this case, used primarily to notify users when an invalid file was chosen to be loaded, when a user has not submitted responses to every question before trying to display their results, and when the user attempts to reset the quiz when they have not answered any questions yet.

           Input: text to be displayed in popup dialog <string>
           Output: none
        """
        # Initialize widgets + layouts
        self.popupTest1 = QDialog(None, Qt.SplashScreen)
        self.popupTest1.OKButton = QPushButton("OK")
        self.popupTest1.mainText = QLabel(text)
        self.popupTest1.mainLayout = QVBoxLayout()
        self.popupTest1.OKButton.clicked.connect(self.popupTest1.close)

        # Customize dialog box appearance (style sheet)
        self.boxStyle = """QDialog{
            border: 1px solid gray;
            border-radius: 5px;
            }"""
        self.popupTest1.setStyleSheet(self.boxStyle)

        # Populate layouts
        self.popupTest1.mainLayout.addWidget(self.popupTest1.mainText, alignment = Qt.AlignCenter)
        self.popupTest1.mainLayout.addWidget(self.popupTest1.OKButton, alignment = Qt.AlignCenter)
        self.popupTest1.setLayout(self.popupTest1.mainLayout)

        self.popupTest1.exec_()

    def tallyResults(self):
        """When the user has answered all questions and clicks the "Submit" button, their results will be tallied.
           If any response has yet to be completed, abort and display a popup box telling the user to answer all questions.

           Input: none
           Output: none
        """
        # Tallies for each response (originally 'west' and 'east)
        self.westTally = 0
        self.eastTally = 0
        self.finalVerdict = 0
        # Algorithm: check if 'west' or 'east', then add corresponding whichPressed() value to correct tally
        # Then return which is bigger (if tie, random)
        for question in self.radioButtonsArray:
            if (question.getWhichButtonPressed() == -1):
                self.popupBox("Not all questions have been answered yet!")
                return 0
            elif (question.getCoast() == 0):        # If question is for 'west'
                self.westTally += question.getWhichButtonPressed()
            elif (question.getCoast() == 1):        # If question is for 'east'
                self.eastTally += question.getWhichButtonPressed()
        # Compare final results, declare winner
        if (self.eastTally == self.westTally):      # Tie case
            self.finalVerdict = randint(1, 2)
        elif (self.eastTally > self.westTally):     # 'East' win case
            self.finalVerdict = 2
        else:                                       # 'West' win case
            self.finalVerdict = 1
        self.signalChangeStack.emit(self.finalVerdict) # Signal to mainWidget who the winner is
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())

    def resetQuestionButtons(self):
        """Reset questions in the event of the user clicking "retake quiz"."""
        for button in self.radioButtonsArray:
            button.resetButtons()
            self.signalResetWidget.emit(0)
        # Reset scroll position to top of screen
        self.scrollArea.verticalScrollBar().setValue(0)
        # Change stacked layout to show pre-results "Submit" button
        self.stackedBottom.setCurrentIndex(0)

    def saveProgress(self):
        """Save progress via writing a text file with relevant save information.

           Input: None
           Output: None
        """
        # First, update the array with which questions have already been answered
        self.updateArrayWhichPressed()
        # Use QFileDialog to grab path to write to
        self.fileDialog = QFileDialog()
        self.path = self.fileDialog.getSaveFileName(parent=self, filter="Text files (*.txt)", directory = os.getcwd())[0]
        if (self.path == ""):
            return()
        # Make sure extension is .txt; if not, make it so
        if not (self.path.endswith(".txt")):
            self.path += ".txt"
        with open(self.path, 'w') as OUTFILE:
            # First line of file = questionnaire index
            OUTFILE.write(str(self.questionnaireIndex) + "\n")
            # Format: questionnaire index <int>
            for question in self.questionsArray:
                lineToWrite = str(question[3]) + "," + str(question[2]) + "\n"
                OUTFILE.write(lineToWrite)

    def updateArrayWhichPressed(self):
        """Update which buttons have been pressed on which responses; used for save/load purposes.

           Input: none
           Output: none
        """
        for i, question in enumerate(self.radioButtonsArray):
            self.questionsArray[i][2] = question.getWhichButtonPressed()

def main():
    app = App()
    progressBarVal = 0
    sys.exit(app.exec_())

if (__name__ == "__main__"):
    main()
