import SwiftUI

struct PressableButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label


            .contentShape(Rectangle())
            .scaleEffect(configuration.isPressed ? 0.98 : 1.0)
            .opacity(configuration.isPressed ? 0.88 : 1.0)
            .brightness(configuration.isPressed ? -0.01 : 0)
            .animation(.easeOut(duration: 0.08), value: configuration.isPressed)
    }
}
