CREATE DATABASE IF NOT EXISTS sgs_db;
USE sgs_db;

CREATE TABLE Rol (
    id_rol INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50)
);

CREATE TABLE Usuario (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    id_rol INT,
    FOREIGN KEY (id_rol) REFERENCES Rol(id_rol)
);

CREATE TABLE Administrador (
    id_admin INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

CREATE TABLE Operador (
    id_interno INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100),
    correo VARCHAR(100)
);

CREATE TABLE Docente (
    id_docente INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100),
    correo VARCHAR(100),
    telefono VARCHAR(20)
);

CREATE TABLE Salon (
    id_salon INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50),
    capacidad INT,
    estado VARCHAR(20) DEFAULT 'disponible',
    ubicacion VARCHAR(100)
);

CREATE TABLE Reserva (
    id_reserva INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATE,
    hora_inicio TIME,
    hora_fin TIME,
    estado VARCHAR(30), -- 'confirmada', 'cancelada', 'pendiente_confirmacion'
    id_docente INT,
    id_salon INT,
    id_operador INT,
    fecha_notificacion DATETIME NULL,
    FOREIGN KEY (id_docente) REFERENCES Docente(id_docente),
    FOREIGN KEY (id_salon) REFERENCES Salon(id_salon),
    FOREIGN KEY (id_operador) REFERENCES Operador(id_interno)
);

CREATE TABLE ColaEspera (
    id_cola INT PRIMARY KEY AUTO_INCREMENT,
    id_salon INT,
    id_docente INT,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_salon) REFERENCES Salon(id_salon),
    FOREIGN KEY (id_docente) REFERENCES Docente(id_docente)
);

INSERT INTO Rol (nombre) VALUES ('Administrador'), ('Operador'), ('Docente');

-- Insertar datos base para que la tabla no aparezca vacía
INSERT INTO Docente (nombre, correo, telefono) VALUES ('Dr. Roberto Gómez', 'roberto@uc.edu', '123456');
INSERT INTO Salon (nombre, capacidad, estado, ubicacion) VALUES ('Laboratorio de Redes', 30, 'disponible', 'Piso 3');
INSERT INTO Reserva (fecha, hora_inicio, hora_fin, estado, id_docente, id_salon) 
VALUES (CURDATE(), '14:00', '16:00', 'confirmada', 1, 1);