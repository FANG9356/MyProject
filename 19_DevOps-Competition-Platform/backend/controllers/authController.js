const db = require("../config/db");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const fs = require("fs"); //  นำเข้า File System (ใช้จัดการไฟล์)
const path = require("path"); //  นำเข้า Path (ใช้จัดการเส้นทางไฟล์)
const { validationResult } = require("express-validator");

exports.login = async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      status: "error",
      message: errors.array()[0].msg,
    });
  }
  try {
    const { username, password } = req.body;

    const [users] = await db.query("SELECT * FROM users WHERE username = ?", [
      username,
    ]);

    if (users.length === 0) {
      return res.status(401).json({
        status: "error",
        message: "ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง",
      });
    }

    const user = users[0];

    if (user.status === "Inactive") {
      return res.status(403).json({
        status: "error",
        message: "บัญชีนี้ถูกระงับการใช้งานชั่วคราว กรุณาติดต่อผู้ดูแลระบบ",
      });
    }

    const isPasswordMatch = await bcrypt.compare(password, user.password);

    if (!isPasswordMatch) {
      return res.status(401).json({
        status: "error",
        message: "ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง (Unauthorized)",
      });
    }

    const payload = {
      id: user.id,
      role: user.role, // เช่น 'admin' หรือ 'user'
    };

    const token = jwt.sign(payload, process.env.JWT_SECRET, {
      expiresIn: process.env.JWT_EXPIRES_IN,
    });

    return res.status(200).json({
      status: "success",
      message: "เข้าสู่ระบบสำเร็จ",
      user: {
        id: user.id,
        name: user.name,
        profile_image: user.profile_image,
        username: user.username,
        role: user.role,
      },
      token: token,
    });
  } catch (error) {
    console.error("Login Error:", error);
    return res.status(500).json({
      status: "error",
      message: "เกิดข้อผิดพลาดที่เซิร์ฟเวอร์",
    });
  }
};

exports.register = async (req, res) => {
  try {
    const { name, username, password, role } = req.body;

    if (!username || !password) {
      return res.status(400).json({
        status: "error",
        message: "กรุณากรอก Username และ Password",
      });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const userRole = role || "admin";

    const [result] = await db.query(
      "INSERT INTO users (name, username, password, role) VALUES (?, ?, ?, ?)",
      [name, username, hashedPassword, userRole],
    );

    return res.status(201).json({
      status: "success",
      message: "สร้างบัญชีผู้ใช้งานสำเร็จ!",
      data: {
        userId: result.insertId,
        username: username,
        role: userRole,
      },
    });
  } catch (error) {
    console.error("Register Error:", error);
    if (error.code === "ER_DUP_ENTRY") {
      return res
        .status(400)
        .json({ status: "error", message: "ชื่อผู้ใช้งานนี้มีในระบบแล้ว" });
    }
    return res
      .status(500)
      .json({ status: "error", message: "เกิดข้อผิดพลาดที่เซิร์ฟเวอร์" });
  }
};

exports.getProfile = async (req, res) => {
  try {
    const userId = req.user.id;

    const [users] = await db.query(
      "SELECT id, name, profile_image, username, role, created_at FROM users WHERE id = ?",
      [userId],
    );

    if (users.length === 0) {
      return res
        .status(404)
        .json({ status: "error", message: "ไม่พบข้อมูลผู้ใช้" });
    }

    return res.status(200).json({
      status: "success",
      user: users[0],
    });
  } catch (error) {
    console.error("Profile Error:", error);
    return res
      .status(500)
      .json({ status: "error", message: "เกิดข้อผิดพลาดที่เซิร์ฟเวอร์" });
  }
};

exports.updateProfile = async (req, res) => {
  try {
    const userId = req.user.id; // ได้มาจาก authMiddleware
    const { name, password } = req.body;
    const [users] = await db.query(
      "SELECT profile_image FROM users WHERE id = ?",
      [userId],
    );
    const oldImage = users.length > 0 ? users[0].profile_image : null;

    let updateFields = [];
    let queryValues = [];

    if (name) {
      updateFields.push("name = ?");
      queryValues.push(name);
    }

    if (password) {
      const hashedPassword = await bcrypt.hash(password, 10);
      updateFields.push("password = ?");
      queryValues.push(hashedPassword);
    }

    if (req.file) {
      const imageUrl = `uploads/${req.file.filename}`;
      updateFields.push("profile_image = ?");
      queryValues.push(imageUrl);

      if (oldImage) {
        const oldImagePath = path.join(__dirname, "../", oldImage);

        if (fs.existsSync(oldImagePath)) {
          fs.unlinkSync(oldImagePath); //  สั่งลบไฟล์ทิ้งทันที!
          console.log(" ลบรูปโปรไฟล์เก่าทิ้งเรียบร้อย:", oldImage);
        }
      }
    }

    if (updateFields.length === 0) {
      return res
        .status(400)
        .json({ status: "error", message: "ไม่มีข้อมูลสำหรับอัปเดต" });
    }

    const sql = `UPDATE users SET ${updateFields.join(", ")} WHERE id = ?`;
    queryValues.push(userId);

    await db.query(sql, queryValues);

    const newImageUrl = req.file ? `uploads/${req.file.filename}` : null;

    return res.status(200).json({
      status: "success",
      message: "อัปเดตข้อมูลโปรไฟล์เรียบร้อยแล้ว",
      newImage: newImageUrl,
    });
  } catch (error) {
    console.error("Update Profile Error:", error);
    return res
      .status(500)
      .json({ status: "error", message: "เกิดข้อผิดพลาดในการอัปเดตข้อมูล" });
  }
};