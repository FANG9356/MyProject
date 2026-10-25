const bcrypt = require("bcryptjs");
const db = require("../config/db");
const fs = require("fs");
const path = require("path");

exports.getAllUsers = async (req, res) => {
  try {
    const myRole = req.user.role;

    let sql = "SELECT id, name, username, status, role FROM users";
    let queryValues = [];

    if (myRole !== "admin") {
      sql += " WHERE role != 'admin'";
    }

    sql += " ORDER BY id DESC";
    const [users] = await db.query(sql, queryValues);

    return res.status(200).json({
      status: "success",
      users: users,
    });
  } catch (error) {
    console.error("Get Users Error:", error);
    return res
      .status(500)
      .json({ status: "error", message: "ไม่สามารถดึงข้อมูลผู้ใช้งานได้" });
  }
};

exports.createUser = async (req, res) => {
  try {
    const { name, username, role, status } = req.body;

    const defaultPassword = await bcrypt.hash("1234", 10);

    const [result] = await db.query(
      "INSERT INTO users (name, username, password, role, status) VALUES (?, ?, ?, ?, ?)",
      [name, username, defaultPassword, role || "user", status || "Active"],
    );

    return res.status(201).json({
      status: "success",
      message: "เพิ่มผู้ใช้งานเรียบร้อยแล้ว (รหัสผ่านเริ่มต้น: 123456)",
      data: { id: result.insertId },
    });
  } catch (error) {
    console.error("Create User Error:", error);
    if (error.code === "ER_DUP_ENTRY") {
      return res.status(400).json({
        status: "error",
        message: "ชื่อผู้ใช้งาน (Username) นี้มีในระบบแล้ว",
      });
    }
    return res
      .status(500)
      .json({ status: "error", message: "เกิดข้อผิดพลาดในการเพิ่มข้อมูล" });
  }
};

exports.updateUser = async (req, res) => {
  try {
    const { id } = req.params;
    const { name, role, status } = req.body;

    await db.query(
      "UPDATE users SET name = ?, role = ?, status = ? WHERE id = ?",
      [name, role, status, id],
    );

    return res.status(200).json({
      status: "success",
      message: "อัปเดตข้อมูลผู้ใช้งานเรียบร้อยแล้ว",
    });
  } catch (error) {
    console.error("Update User Error:", error);
    if (error.code === "ER_DUP_ENTRY") {
      return res.status(400).json({
        status: "error",
        message: "ชื่อผู้ใช้งาน (Username) นี้ถูกใช้ไปแล้ว",
      });
    }
    return res
      .status(500)
      .json({ status: "error", message: "เกิดข้อผิดพลาดในการอัปเดตข้อมูล" });
  }
};

exports.deleteUser = async (req, res) => {
  try {
    const { id } = req.params;

    const [users] = await db.query(
      "SELECT profile_image FROM users WHERE id = ?",
      [id],
    );
    const userImage = users.length > 0 ? users[0].profile_image : null;

    await db.query("DELETE FROM users WHERE id = ?", [id]);

    if (userImage) {
      const imagePath = path.join(__dirname, "../", userImage);

      if (fs.existsSync(imagePath)) {
        fs.unlinkSync(imagePath);
        console.log(" ลบไฟล์รูปภาพขยะเรียบร้อย:", userImage);
      }
    }

    return res.status(200).json({
      status: "success",
      message: "ลบข้อมูลผู้ใช้งานเรียบร้อยแล้ว",
    });
  } catch (error) {
    console.error("Delete User Error:", error);
    return res
      .status(500)
      .json({ status: "error", message: "เกิดข้อผิดพลาดในการลบข้อมูล" });
  }
};
