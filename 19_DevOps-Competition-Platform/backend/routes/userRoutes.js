const express = require("express");
const router = express.Router();
const userController = require("../controllers/userController");

const verifyToken = require("../middlewares/authMiddleware");

router.get("/", verifyToken, userController.getAllUsers);
router.post("/", verifyToken, userController.createUser);
router.put("/:id", verifyToken, userController.updateUser);
router.delete("/:id", verifyToken, userController.deleteUser);

const fs = require("fs");
const path = require("path");
router.post("/test-unlink", (req, res) => {
  try {
    const { filename } = req.body;

    if (!filename) {
      return res.status(400).json({
        status: "error",
        message:
          'กรุณาส่งชื่อไฟล์มาใน req.body ด้วยครับ เช่น { "filename": "test.jpg" }',
      });
    }

    const targetPath = path.join(__dirname, "../uploads", filename);

    if (fs.existsSync(targetPath)) {
      fs.unlinkSync(targetPath);

      return res.status(200).json({
        status: "success",
        message: ` ลบไฟล์ ${filename} สำเร็จแล้ว!`,
        deletedPath: targetPath,
      });
    } else {
      return res.status(404).json({
        status: "error",
        message: ` หาไฟล์ไม่เจอครับ ลองเช็ค Path ดูนะ`,
        checkedPath: targetPath,
      });
    }
  } catch (error) {
    console.error("Test Unlink Error:", error);
    return res.status(500).json({
      status: "error",
      message: "ระบบลบไฟล์มีปัญหา",
      error: error.message,
    });
  }
});

module.exports = router;
