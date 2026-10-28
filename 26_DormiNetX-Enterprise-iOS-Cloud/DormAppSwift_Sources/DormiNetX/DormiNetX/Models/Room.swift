import Foundation
import SwiftData

@Model
final class Room: Identifiable {
    @Attribute(.unique) var id: UUID = UUID()
    var serverId: Int?


    var ownerAccountID: Int?

    var roomNumber: String = ""
    var roomType: String = ""


    var lastUpdated: Date = Date()
    var isDirty: Bool = false
    var isDeletedLocally: Bool = false

    init(serverId: Int? = nil, roomNumber: String = "", roomType: String = "", ownerAccountID: Int? = nil) {
        self.serverId = serverId
        self.roomNumber = roomNumber
        self.roomType = roomType
        self.ownerAccountID = ownerAccountID
    }
}
