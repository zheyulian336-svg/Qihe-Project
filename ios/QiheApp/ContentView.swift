import SwiftUI

struct ContentView: View {
    var body: some View {
        ZStack {
            Color(red: 0.92, green: 0.94, blue: 0.98)
                .ignoresSafeArea(.all)
            WebViewWrapper()
                .ignoresSafeArea(edges: .bottom)
        }
    }
}
