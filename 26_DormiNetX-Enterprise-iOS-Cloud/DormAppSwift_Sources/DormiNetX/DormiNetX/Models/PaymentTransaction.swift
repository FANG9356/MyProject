import Foundation
import SwiftData


@Model
final class PaymentTransaction: Identifiable {
    @Attribute(.unique) var id: UUID = UUID()
    var paymentID: UUID = UUID()
    var amount: Double = 0
    var occurredAt: Date = Date()
    var method: String = ""
    var kind: String = "payment"
    var note: String = ""
    var slipPaths: [String] = []
    var source: String = ""
    var lastUpdated: Date = Date()
    var isDirty: Bool = true

    init(paymentID: UUID, amount: Double, occurredAt: Date = Date(), method: String = "", source: String = "") {
        self.paymentID = paymentID
        self.amount = amount
        self.occurredAt = occurredAt
        self.method = method
        self.source = source
        self.lastUpdated = occurredAt
    }
}
