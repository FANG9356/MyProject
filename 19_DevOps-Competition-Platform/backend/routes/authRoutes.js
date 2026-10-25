const express = require("express");
const router = express.Router();
const { body } = require("express-validator");
const authController = require("../controllers/authController");

const verifyToken = require("../middlewares/authMiddleware");
const upload = require("../middlewares/uploadMiddleware");

router.post("/register", authController.register);
router.post(
  "/login",
  [
    body("username").notEmpty().withMessage("กรุณากรอก Username").trim(),
    body("password")
      .isLength({ min: 4 })
      .withMessage("รหัสผ่านต้องมีอย่างน้อย 4 ตัวอักษร"),
  ],
  authController.login,
);

router.get("/profile", verifyToken, authController.getProfile);
router.put(
  "/profile",
  verifyToken,
  upload.single("profile_image"),
  authController.updateProfile,
);

module.exports = router;