import SwiftUI
import SwiftData

struct ContentView: View {
    @AppStorage("isLoggedIn") var isLoggedIn: Bool = false
    @Environment(\.modelContext) private var context

    private var isGuestContainer: Bool {
        context.container.configurations.first?.url.absoluteString == "file:///dev/null" ||
        context.container.configurations.first?.isStoredInMemoryOnly == true
    }

    var body: some View {
        ZStack {

            GlassBackgroundView()
                .ignoresSafeArea(.all)

            if isLoggedIn && !isGuestContainer {
                RoomListView()

                    .transition(.opacity)
            } else {
                LoginView()
                    .transition(.opacity)
            }
        }

        .animation(.easeInOut(duration: 0.8), value: isLoggedIn && !isGuestContainer)
    }
}
