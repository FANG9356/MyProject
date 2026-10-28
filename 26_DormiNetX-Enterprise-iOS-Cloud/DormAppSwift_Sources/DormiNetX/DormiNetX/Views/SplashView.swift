import SwiftUI
import CoreText


struct TwinBuildingsOutline: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()

        let tallW: CGFloat = 52
        let gap: CGFloat = 6
        let smallW: CGFloat = 28
        let scaleX = rect.width / 86

        let smallH: CGFloat = 76
        let scaleY = rect.height / 100

        let r: CGFloat = 8


        path.move(to: CGPoint(x: 0, y: 100 * scaleY))


        path.addLine(to: CGPoint(x: 0, y: r * scaleY))
        path.addQuadCurve(to: CGPoint(x: r * scaleX, y: 0), control: CGPoint(x: 0, y: 0))


        path.addLine(to: CGPoint(x: (tallW - r) * scaleX, y: 0))
        path.addQuadCurve(to: CGPoint(x: tallW * scaleX, y: r * scaleY), control: CGPoint(x: tallW * scaleX, y: 0))


        path.addLine(to: CGPoint(x: tallW * scaleX, y: 100 * scaleY))


        let smallStartX = tallW + gap
        path.addLine(to: CGPoint(x: smallStartX * scaleX, y: 100 * scaleY))


        let smallTopY = 100 - smallH
        path.addLine(to: CGPoint(x: smallStartX * scaleX, y: (smallTopY + r) * scaleY))
        path.addQuadCurve(to: CGPoint(x: (smallStartX + r) * scaleX, y: smallTopY * scaleY),
                          control: CGPoint(x: smallStartX * scaleX, y: smallTopY * scaleY))


        let smallEndX = smallStartX + smallW
        path.addLine(to: CGPoint(x: (smallEndX - r) * scaleX, y: smallTopY * scaleY))
        path.addQuadCurve(to: CGPoint(x: smallEndX * scaleX, y: (smallTopY + r) * scaleY),
                          control: CGPoint(x: smallEndX * scaleX, y: smallTopY * scaleY))


        path.addLine(to: CGPoint(x: smallEndX * scaleX, y: 100 * scaleY))

        return path
    }
}

private struct SplashPalette {
    let backgroundTop: Color
    let backgroundBottom: Color
    let primaryStroke: Color
    let windowFill: Color
    let glow: Color

    init(isDark: Bool) {
        if isDark {
            backgroundTop = Color(red: 0.10, green: 0.10, blue: 0.14)
            backgroundBottom = Color(red: 0.15, green: 0.14, blue: 0.19)
            primaryStroke = .white
            windowFill = Color(red: 0.32, green: 0.32, blue: 0.36)
            glow = Color.white.opacity(0.22)
        } else {
            backgroundTop = Color(red: 0.95, green: 0.96, blue: 0.98)
            backgroundBottom = Color(red: 0.88, green: 0.91, blue: 0.97)
            primaryStroke = .indigo
            windowFill = .indigo
            glow = Color.indigo.opacity(0.18)
        }
    }
}

struct SplashView: View {
    @AppStorage("appTheme") private var appTheme: Int = AppTheme.system.rawValue
    @Environment(\.colorScheme) private var colorScheme
    @State private var isActive = false


    let scatteredOffsets: [CGSize] = [
        CGSize(width: -200, height: -250),
        CGSize(width: -100, height: -300),
        CGSize(width: -250, height: -80),
        CGSize(width: -150, height: -120),
        CGSize(width: -300, height: 80),
        CGSize(width: -200, height: 100),
        CGSize(width: -250, height: 250),
        CGSize(width: -100, height: 200)
    ]
    @State private var dotOffsets: [CGSize] = []
    @State private var dotOpacities: [Double] = Array(repeating: 0.0, count: 8)


    let scatteredOffsets2: [CGSize] = [
        CGSize(width: 250, height: -200),
        CGSize(width: 200, height: 50),
        CGSize(width: 300, height: 250)
    ]
    @State private var dotOffsets2: [CGSize] = []
    @State private var dotOpacities2: [Double] = Array(repeating: 0.0, count: 3)


    @State private var outlineProgress: CGFloat = 0.0


    @State private var textOutlineProgress: CGFloat = 0.0
    @State private var textOpacity: Double = 1.0

    init() {
        _dotOffsets = State(initialValue: scatteredOffsets)
        _dotOffsets2 = State(initialValue: scatteredOffsets2)
    }

    private var resolvedColorScheme: ColorScheme {
        (AppTheme(rawValue: appTheme)?.colorScheme) ?? colorScheme
    }

    private var palette: SplashPalette {
        SplashPalette(isDark: resolvedColorScheme == .dark)
    }

    var body: some View {
        ZStack {
            if isActive {
                ContentView()
                    .transition(.opacity)
            } else {
                ZStack {

                    LinearGradient(
                        colors: [palette.backgroundTop, palette.backgroundBottom],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                    .ignoresSafeArea()


                    VStack(spacing: 24) {

                        ZStack(alignment: .bottomLeading) {


                            LazyVGrid(columns: [GridItem(.fixed(16)), GridItem(.fixed(16))], spacing: 10) {
                                ForEach(0..<8, id: \.self) { index in
                                    RoundedRectangle(cornerRadius: 3)
                                        .fill(palette.windowFill)
                                        .frame(width: 14, height: 14)
                                        .offset(dotOffsets[index])
                                        .opacity(dotOpacities[index])
                                }
                            }
                            .frame(width: 38, height: 86)
                            .offset(x: 7, y: -7)


                            LazyVGrid(columns: [GridItem(.fixed(16))], spacing: 10) {
                                ForEach(0..<3, id: \.self) { index in
                                    RoundedRectangle(cornerRadius: 3)
                                        .fill(palette.windowFill)
                                        .frame(width: 14, height: 14)
                                        .offset(dotOffsets2[index])
                                        .opacity(dotOpacities2[index])
                                }
                            }
                            .frame(width: 14, height: 62)
                            .offset(x: 65, y: -7)


                            TwinBuildingsOutline()
                                .trim(from: 0, to: outlineProgress)
                                .stroke(palette.primaryStroke, style: StrokeStyle(lineWidth: 4, lineCap: .round, lineJoin: .round))
                                .frame(width: 86, height: 100)
                                .shadow(color: palette.glow, radius: 12, x: 0, y: 4)
                        }


                        ContinuousDormiNetShape()
                            .trim(from: 0, to: textOutlineProgress)
                            .stroke(palette.primaryStroke, style: StrokeStyle(lineWidth: 3, lineCap: .round, lineJoin: .round))
                            .frame(width: 160, height: 26)
                            .opacity(textOpacity)
                            .shadow(color: palette.glow, radius: 8, x: 0, y: 3)
                    }
                }
                .transition(.opacity)
                .onAppear {

                    for i in 0..<8 {
                        withAnimation(.spring(response: 0.9, dampingFraction: 0.7).delay(Double(i) * 0.08)) {
                            dotOffsets[i] = .zero
                            dotOpacities[i] = 1.0
                        }
                    }
                    for i in 0..<3 {
                        withAnimation(.spring(response: 0.9, dampingFraction: 0.7).delay(Double(i) * 0.12 + 0.2)) {
                            dotOffsets2[i] = .zero
                            dotOpacities2[i] = 1.0
                        }
                    }


                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                        withAnimation(.easeInOut(duration: 1.5)) {
                            outlineProgress = 1.0
                        }

                        withAnimation(.easeInOut(duration: 3.0).delay(0.2)) {
                            textOutlineProgress = 1.0
                        }
                    }


                    DispatchQueue.main.asyncAfter(deadline: .now() + 5.2) {

                        withAnimation(.easeInOut(duration: 1.2)) {
                            outlineProgress = 0.0
                            textOutlineProgress = 0.0
                        }


                        withAnimation(.easeIn(duration: 0.4)) {
                            textOpacity = 0.0
                        }


                        for i in 0..<8 {
                            withAnimation(.spring(response: 0.9, dampingFraction: 0.8).delay(Double(7 - i) * 0.05)) {
                                dotOffsets[i] = scatteredOffsets[i]
                                dotOpacities[i] = 0.0
                            }
                        }

                        for i in 0..<3 {
                            withAnimation(.spring(response: 0.9, dampingFraction: 0.8).delay(Double(2 - i) * 0.07)) {
                                dotOffsets2[i] = scatteredOffsets2[i]
                                dotOpacities2[i] = 0.0
                            }
                        }
                    }


                    DispatchQueue.main.asyncAfter(deadline: .now() + 7.0) {
                        isActive = true
                    }
                }
            }
        }

        .animation(.easeInOut(duration: 1.2), value: isActive)
    }
}


struct ContinuousDormiNetShape: Shape {
    func path(in rect: CGRect) -> Path {
        var p = Path()

        let scale = rect.height / 10.0
        let w = scale


        func pt(_ x: CGFloat, _ y: CGFloat) -> CGPoint {
            return CGPoint(x: x * w, y: y * scale)
        }

        p.move(to: pt(0, 10))


        p.addLine(to: pt(0, 0))
        p.addLine(to: pt(4, 0))
        p.addQuadCurve(to: pt(6, 2), control: pt(6, 0))
        p.addLine(to: pt(6, 8))
        p.addQuadCurve(to: pt(4, 10), control: pt(6, 10))
        p.addLine(to: pt(0, 10))


        p.addLine(to: pt(8, 10))


        p.addLine(to: pt(8, 5))
        p.addLine(to: pt(12, 5))
        p.addLine(to: pt(12, 10))
        p.addLine(to: pt(8, 10))
        p.addLine(to: pt(12, 10))


        p.addLine(to: pt(14, 10))


        p.addLine(to: pt(14, 5))
        p.addLine(to: pt(17, 5))
        p.addLine(to: pt(14, 5))
        p.addLine(to: pt(14, 10))
        p.addLine(to: pt(17, 10))


        p.addLine(to: pt(19, 10))


        p.addLine(to: pt(19, 5))
        p.addLine(to: pt(22, 5))
        p.addLine(to: pt(22, 10))
        p.addLine(to: pt(22, 5))
        p.addLine(to: pt(25, 5))
        p.addLine(to: pt(25, 10))


        p.addLine(to: pt(27, 10))


        p.addLine(to: pt(27, 2))
        p.addLine(to: pt(27, 10))


        p.addLine(to: pt(29, 10))


        p.addLine(to: pt(29, 0))
        p.addLine(to: pt(35, 10))
        p.addLine(to: pt(35, 0))
        p.addLine(to: pt(35, 10))


        p.addLine(to: pt(37, 10))


        p.addLine(to: pt(41, 10))
        p.addLine(to: pt(41, 5))
        p.addLine(to: pt(37, 5))
        p.addLine(to: pt(37, 7.5))
        p.addLine(to: pt(40, 7.5))
        p.addLine(to: pt(37, 7.5))
        p.addLine(to: pt(37, 10))
        p.addLine(to: pt(41, 10))


        p.addLine(to: pt(43, 10))


        p.addLine(to: pt(43, 1))
        p.addLine(to: pt(43, 5))
        p.addLine(to: pt(41.5, 5))
        p.addLine(to: pt(45, 5))
        p.addLine(to: pt(43, 5))
        p.addLine(to: pt(43, 10))
        p.addLine(to: pt(45.5, 10))


        let pathWidth = 45.5 * w
        let offset = (rect.width - pathWidth) / 2
        let transform = CGAffineTransform(translationX: offset, y: 0)

        return p.applying(transform)
    }
}
