package logger

import (
	"fmt"
	"os"
	"time"

	"github.com/briandowns/spinner"
	"github.com/fatih/color"
)

var (
	spin         = spinner.New(spinner.CharSets[2], 100*time.Millisecond, spinner.WithWriter(os.Stderr))
	loggingLevel = InfoLevel
)

func SetLoggingLevel(level LoggingLevel) {
	loggingLevel = level
}

func GetLoggingLevel() LoggingLevel {
	return loggingLevel
}

type LoggingLevel int

const (
	ErrorLevel LoggingLevel = iota
	WarnLevel
	InfoLevel
	DebugLevel
)

func Errorf(format string, a ...interface{}) {
	if loggingLevel >= ErrorLevel {
		printlnStderr(color.RedString(format, a...))
	}
}

func Warnf(format string, a ...interface{}) {
	if loggingLevel >= WarnLevel {
		printlnStderr(color.YellowString(format, a...))
	}
}

func Infof(format string, a ...interface{}) {
	if loggingLevel >= InfoLevel {
		printlnStderr(fmt.Sprintf(format, a...))
	}
}

func Debugf(format string, a ...interface{}) {
	if loggingLevel >= DebugLevel {
		printlnStderr(color.WhiteString(format, a...))
	}
}

func NewLine() {
	printlnStderr("")
}

func printlnStderr(message string) {
	StopSpinner()
	_, err := fmt.Fprintln(os.Stderr, message)
	if err != nil {
		panic(err)
	}
}

func StopSpinner() {
	StopSpinnerWithFinalMessage("")
}

func StopSpinnerWithFinalMessage(format string, a ...interface{}) {
	if spin.Active() {
		if format != "" {
			spin.FinalMSG = fmt.Sprintf("\r%s  \n", fmt.Sprintf(format, a...))
		}
		spin.Stop()
	}
}

func StopSpinnerWithFinalWarning(format string, a ...interface{}) {
	StopSpinnerWithFinalMessage(fmt.Sprintf(color.YellowString(format, a...)))
}

func InfoSpinnerf(format string, a ...interface{}) {
	if loggingLevel >= InfoLevel {
		StopSpinner()
		infoString := fmt.Sprintf(format, a...)
		spin = spinner.New(
			spinner.CharSets[2],
			100*time.Millisecond,
			spinner.WithWriter(os.Stderr),
			spinner.WithSuffix(fmt.Sprintf(" %s", infoString)),
			spinner.WithFinalMSG(fmt.Sprintf("\r%s  \n", infoString)),
		)
		spin.Start()
	}
}
