export interface Role {
  id: number;
  nombre: string;
  descripcion?: string;
}

export interface Usuario {
  id?: number;              // Opcional porque el backend lo asigna automáticamente al crear un nuevo usuario
  email: string;
  nombre: string;
  apellido?: string;        // Opcional por retrocompatibilidad, no gestionado por backend
  dni: string;
  fecha_nacimiento: string; // Angular maneja las fechas que vienen del backend como strings 'YYYY-MM-DD'
  rol?: Role | any;         // Objeto rol o ID del rol
  rol_id?: number | null;   // ID del rol para peticiones de escritura
  password?: string;        // Opcional al crear usuario, ignorado al editar
  is_active?: boolean;      // Estado de activación en el sistema
  is_superuser?: boolean;   // Jerarquía de Super Administrador (ADR-0008)
}
