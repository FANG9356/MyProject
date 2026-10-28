import XCTest

final class BillingUITests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testPartialPaymentFlow() throws {
        let app = XCUIApplication()
        app.launch()


        let billsTab = app.buttons["Tab_bills"]
        guard billsTab.waitForExistence(timeout: 5) else { return }
        billsTab.tap()


        let firstBill = app.buttons.matching(identifier: "BillRow").firstMatch
        if firstBill.waitForExistence(timeout: 3) {
            firstBill.tap()


            let partialPayButton = app.buttons["PartialPaymentButton"]
            if partialPayButton.waitForExistence(timeout: 2) {
                partialPayButton.tap()

                let amountField = app.textFields["PaymentAmountField"]
                amountField.tap()
                amountField.typeText("1000")

                let saveButton = app.buttons["ConfirmPaymentButton"]
                saveButton.tap()


                XCTAssertTrue(app.staticTexts["บันทึกสำเร็จ"].waitForExistence(timeout: 3))
            }
        }
    }
}
