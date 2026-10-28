import XCTest

final class TenantLifecycleUITests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testAddTenantAndMoveRoom() throws {
        let app = XCUIApplication()
        app.launch()


        let tabBar = app.tabBars["MainTabBar"]
        guard tabBar.waitForExistence(timeout: 5) else { return }


        let tenantsTab = app.buttons["Tab_tenants"]
        tenantsTab.tap()


        let addTenantButton = app.buttons["AddTenantButton"]
        XCTAssertTrue(addTenantButton.waitForExistence(timeout: 3))
        addTenantButton.tap()


        let firstNameField = app.textFields["FirstNameField"]
        XCTAssertTrue(firstNameField.waitForExistence(timeout: 2))
        firstNameField.tap()
        firstNameField.typeText("สมชาย")

        let roomField = app.textFields["RoomNumberField"]
        roomField.tap()
        roomField.typeText("101")


        let saveButton = app.buttons["SaveTenantButton"]
        saveButton.tap()


        let searchField = app.textFields["SearchTenantField"]
        XCTAssertTrue(searchField.waitForExistence(timeout: 3))
        searchField.tap()
        searchField.typeText("101")

        let tenantCard = app.buttons["TenantCard_101"]
        XCTAssertTrue(tenantCard.waitForExistence(timeout: 3))
    }
}
