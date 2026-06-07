import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 1320
    height: 860
    visible: true
    title: "TaskTide Next"
    color: "#f4f6f8"

    property int currentPage: 0

    function statusColor(status) {
        if (status === "выполнена") return "#1f7a57"
        if (status === "в процессе") return "#d27a00"
        return "#515e6b"
    }

    function priorityColor(priority) {
        if (priority.indexOf("Важно - Срочно") >= 0) return "#cf3f2f"
        if (priority.indexOf("Важно - Не срочно") >= 0) return "#1f7a57"
        if (priority.indexOf("Не важно - Срочно") >= 0) return "#d27a00"
        return "#4f5d6a"
    }

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#fdf8f1" }
            GradientStop { position: 1.0; color: "#eef3f7" }
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 18

        Rectangle {
            Layout.preferredWidth: 290
            Layout.fillHeight: true
            radius: 26
            color: "#102a43"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 16

                Label {
                    text: "TaskTide"
                    color: "#fef6e4"
                    font.pixelSize: 34
                    font.bold: true
                    font.family: "Avenir Next"
                }

                Label {
                    text: "Next UI / PySide6 QML"
                    color: "#9fb3c8"
                    font.pixelSize: 14
                    font.family: "Avenir Next"
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 2
                    color: "#243b53"
                }

                Button {
                    text: "Дашборд"
                    Layout.fillWidth: true
                    onClicked: root.currentPage = 0
                    highlighted: root.currentPage === 0
                }
                Button {
                    text: "Задачи"
                    Layout.fillWidth: true
                    onClicked: root.currentPage = 1
                    highlighted: root.currentPage === 1
                }
                Button {
                    text: "Фокус"
                    Layout.fillWidth: true
                    onClicked: root.currentPage = 2
                    highlighted: root.currentPage === 2
                }
                Button {
                    text: "Подзадачи"
                    Layout.fillWidth: true
                    onClicked: root.currentPage = 3
                    highlighted: root.currentPage === 3
                }

                Item { Layout.fillHeight: true }

                Label {
                    text: "Старая версия остаётся в `main.py`"
                    color: "#9fb3c8"
                    wrapMode: Text.WordWrap
                    font.pixelSize: 12
                    font.family: "Avenir Next"
                    Layout.fillWidth: true
                }
            }
        }

        Rectangle {
            Layout.fillHeight: true
            Layout.fillWidth: true
            radius: 26
            color: "#ffffff"
            border.width: 1
            border.color: "#d9e2ec"

            StackLayout {
                anchors.fill: parent
                anchors.margins: 24
                currentIndex: root.currentPage

                Item {
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 16

                        Label {
                            text: "Обзор задач"
                            color: "#102a43"
                            font.pixelSize: 32
                            font.bold: true
                            font.family: "Avenir Next"
                        }

                        RowLayout {
                            spacing: 14
                            Layout.fillWidth: true

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 140
                                radius: 16
                                color: "#102a43"
                                Label {
                                    anchors.centerIn: parent
                                    text: "Всего\n" + bridge.stats.total
                                    color: "#fef6e4"
                                    horizontalAlignment: Text.AlignHCenter
                                    font.pixelSize: 26
                                    font.bold: true
                                    font.family: "Avenir Next"
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 140
                                radius: 16
                                color: "#1f7a57"
                                Label {
                                    anchors.centerIn: parent
                                    text: "Выполнено\n" + bridge.stats.completed
                                    color: "#f4f9f4"
                                    horizontalAlignment: Text.AlignHCenter
                                    font.pixelSize: 26
                                    font.bold: true
                                    font.family: "Avenir Next"
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 140
                                radius: 16
                                color: "#d27a00"
                                Label {
                                    anchors.centerIn: parent
                                    text: "В процессе\n" + bridge.stats.in_progress
                                    color: "#fffaf3"
                                    horizontalAlignment: Text.AlignHCenter
                                    font.pixelSize: 26
                                    font.bold: true
                                    font.family: "Avenir Next"
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 140
                                radius: 16
                                color: "#334e68"
                                Label {
                                    anchors.centerIn: parent
                                    text: "Не начато\n" + bridge.stats.not_started
                                    color: "#f0f4f8"
                                    horizontalAlignment: Text.AlignHCenter
                                    font.pixelSize: 26
                                    font.bold: true
                                    font.family: "Avenir Next"
                                }
                            }
                        }

                        Label {
                            text: "Последние задачи"
                            color: "#243b53"
                            font.pixelSize: 20
                            font.bold: true
                            font.family: "Avenir Next"
                        }

                        ListView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            spacing: 10
                            model: bridge.tasks
                            clip: true

                            delegate: Rectangle {
                                width: ListView.view.width
                                height: 94
                                radius: 14
                                color: "#f8fafc"
                                border.width: 1
                                border.color: "#d9e2ec"

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 14
                                    spacing: 12

                                    Rectangle {
                                        width: 6
                                        radius: 3
                                        Layout.fillHeight: true
                                        color: root.priorityColor(modelData.priority)
                                    }

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 3
                                        Label {
                                            text: modelData.name
                                            font.pixelSize: 18
                                            color: "#102a43"
                                            font.bold: true
                                            font.family: "Avenir Next"
                                            elide: Text.ElideRight
                                        }
                                        Label {
                                            text: modelData.category + "   •   " + modelData.deadline
                                            color: "#486581"
                                            font.pixelSize: 13
                                            font.family: "Avenir Next"
                                        }
                                    }

                                    Rectangle {
                                        radius: 999
                                        color: root.statusColor(modelData.status)
                                        implicitWidth: statusText.implicitWidth + 22
                                        implicitHeight: 34
                                        Label {
                                            id: statusText
                                            anchors.centerIn: parent
                                            text: modelData.status
                                            color: "white"
                                            font.pixelSize: 13
                                            font.bold: true
                                            font.family: "Avenir Next"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                Item {
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 14

                        RowLayout {
                            Layout.fillWidth: true
                            Label {
                                text: "Задачи"
                                color: "#102a43"
                                font.pixelSize: 32
                                font.bold: true
                                font.family: "Avenir Next"
                            }
                            Item { Layout.fillWidth: true }
                            Button {
                                text: "Обновить"
                                onClicked: bridge.refresh()
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            radius: 14
                            color: "#f8fafc"
                            border.width: 1
                            border.color: "#d9e2ec"
                            padding: 14

                            ColumnLayout {
                                anchors.fill: parent
                                spacing: 10

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 10
                                    TextField {
                                        id: nameInput
                                        Layout.fillWidth: true
                                        placeholderText: "Название новой задачи"
                                    }
                                    ComboBox {
                                        id: priorityInput
                                        model: [
                                            "Важно - Срочно",
                                            "Важно - Не срочно",
                                            "Не важно - Срочно",
                                            "Не важно - Не срочно"
                                        ]
                                        Layout.preferredWidth: 220
                                    }
                                    ComboBox {
                                        id: categoryInput
                                        model: ["Работа", "Учёба", "Личное"]
                                        Layout.preferredWidth: 150
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 10
                                    SpinBox {
                                        id: minutesInput
                                        from: 1
                                        to: 525600
                                        value: 60
                                        editable: true
                                        Layout.preferredWidth: 220
                                    }
                                    TextField {
                                        id: descriptionInput
                                        Layout.fillWidth: true
                                        placeholderText: "Короткое описание (опционально)"
                                    }
                                    Button {
                                        text: "Добавить"
                                        onClicked: {
                                            bridge.addTask(
                                                nameInput.text,
                                                priorityInput.currentText,
                                                categoryInput.currentText,
                                                minutesInput.value,
                                                descriptionInput.text
                                            )
                                            nameInput.text = ""
                                            descriptionInput.text = ""
                                        }
                                    }
                                }
                            }
                        }

                        ListView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            spacing: 10
                            clip: true
                            model: bridge.tasks

                            delegate: Rectangle {
                                width: ListView.view.width
                                height: 112
                                radius: 14
                                color: "#ffffff"
                                border.width: 1
                                border.color: "#d9e2ec"

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 14
                                    spacing: 12

                                    Rectangle {
                                        width: 6
                                        radius: 3
                                        Layout.fillHeight: true
                                        color: root.priorityColor(modelData.priority)
                                    }

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 4
                                        Label {
                                            text: modelData.name
                                            font.pixelSize: 18
                                            color: "#102a43"
                                            font.bold: true
                                            font.family: "Avenir Next"
                                            elide: Text.ElideRight
                                        }
                                        Label {
                                            text: modelData.priority + " • " + modelData.category
                                            color: "#486581"
                                            font.pixelSize: 13
                                            font.family: "Avenir Next"
                                        }
                                        Label {
                                            text: "Дедлайн: " + modelData.deadline
                                            color: "#334e68"
                                            font.pixelSize: 13
                                            font.family: "Avenir Next"
                                        }
                                    }

                                    ComboBox {
                                        model: ["не начата", "в процессе", "выполнена"]
                                        currentIndex: {
                                            if (modelData.status === "в процессе") return 1
                                            if (modelData.status === "выполнена") return 2
                                            return 0
                                        }
                                        onActivated: bridge.setTaskStatus(modelData.id, currentText)
                                        Layout.preferredWidth: 170
                                    }

                                    Button {
                                        text: "Удалить"
                                        onClicked: bridge.removeTask(modelData.id)
                                    }
                                }
                            }
                        }
                    }
                }

                Item {
                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 12
                        Label {
                            text: "Фокус"
                            color: "#102a43"
                            font.pixelSize: 34
                            font.bold: true
                            font.family: "Avenir Next"
                        }
                        Label {
                            text: "Следующий шаг: перенести Pomodoro-экран в QML."
                            color: "#486581"
                            font.pixelSize: 16
                            font.family: "Avenir Next"
                        }
                    }
                }

                Item {
                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 12
                        Label {
                            text: "Подзадачи"
                            color: "#102a43"
                            font.pixelSize: 34
                            font.bold: true
                            font.family: "Avenir Next"
                        }
                        Label {
                            text: "Следующий шаг: перенести иерархические заметки в QML."
                            color: "#486581"
                            font.pixelSize: 16
                            font.family: "Avenir Next"
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: bridge.refresh()
}
