const jwt = require('jsonwebtoken');

const verifyToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({
            status: 'error',
            message: 'ไม่มีสิทธิ์เข้าถึง (Unauthorized): กรุณาส่ง Token'
        });
    }

    const token = authHeader.split(' ')[1];

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);

        req.user = decoded;

        next(); 
        
    } catch (error) {
        return res.status(401).json({
            status: 'error',
            message: 'Token ไม่ถูกต้อง หรือ หมดอายุการใช้งานแล้ว'
        });
    }
};

module.exports = verifyToken;