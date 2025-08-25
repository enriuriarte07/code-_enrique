import random
import copy

class LaberintoGatoRaton:
    def __init__(self, filas=8, columnas=8):
        self.filas = filas
        self.columnas = columnas
        self.tablero = [['.' for _ in range(columnas)] for _ in range(filas)]
        self.pos_gato = (0, 0)
        self.pos_raton = (filas-1, columnas-1)
        self.turno_raton = True  # True = ratón, False = gato
        self.juego_terminado = False
        self.ganador = None
        self.turnos_transcurridos = 0
        self.max_turnos = 10  # Si el ratón sobrevive 10 turnos, gana
        
        # Colocar piezas en el tablero
        self.actualizar_tablero()
    

    def actualizar_tablero(self):
        # Limpiar tablero
        
        for i in range(self.filas):
            for j in range(self.columnas):
                self.tablero[i][j] = '.'
        
        # Colocar gato y ratón
        self.tablero[self.pos_gato[0]][self.pos_gato[1]] = 'G'
        self.tablero[self.pos_raton[0]][self.pos_raton[1]] = 'R'
    
    def mostrar_tablero(self):
        print("\n  " + ".".join([str(i) for i in range(self.columnas)]))
        for i in range(self.filas):
            fila = f"{i} "
            for j in range(self.columnas):
                fila += f"{self.tablero[i][j]} "
            print(fila)
        
        jugador_actual = "Ratón" if self.turno_raton else "Gato"
        print(f"\nTurno: {self.turnos_transcurridos}/{self.max_turnos}")
        print(f"Jugador actual: {jugador_actual}")
        print(f"Posición Gato: {self.pos_gato}")
        print(f"Posición Ratón: {self.pos_raton}")
    
    def movimientos_validos(self, pos, es_raton=True):
        """Genera movimientos válidos para una posición"""
        movimientos = []
        fila, col = pos
        
        # Direcciones posibles (8 direcciones si es ratón ágil, 4 si es básico)
        if es_raton:
            # El ratón puede moverse en 8 direcciones (¡es ágil!)
            direcciones = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        else:
            # El gato se mueve en 4 direcciones básicas
            direcciones = [(-1,0), (1,0), (0,-1), (0,1),]
        
        for df, dc in direcciones:
            nueva_fila, nueva_col = fila + df, col + dc
            if 0 <= nueva_fila < self.filas and 0 <= nueva_col < self.columnas:
                movimientos.append((nueva_fila, nueva_col))
        
        return movimientos
    
    def distancia_manhattan(self, pos1, pos2):
        """Calcula la distancia Manhattan entre dos posiciones"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def evaluar_posicion(self):
        """Evalúa la posición actual del juego"""
        if self.juego_terminado:
            if self.ganador == "gato":
                return -999
                  # Muy malo para el ratón
            elif self.ganador == "raton":
                return 99   # Muy bueno para el ratón
        
        # Evaluación basada en distancia y turnos restantes
        distancia = self.distancia_manhattan(self.pos_gato, self.pos_raton)
        turnos_restantes = self.max_turnos - self.turnos_transcurridos
        
        # El ratón prefiere estar lejos y que queden muchos turnos
        puntuacion = distancia * 10 + turnos_restantes * 5
        
        # Bonus por estar en las esquinas (más difícil de atrapar)
        if self.pos_raton in [(0,0), (0,self.columnas-1), (self.filas-1,0), (self.filas-1,self.columnas-1)]:
            puntuacion += 5
        
        return puntuacion
    
    def verificar_fin_juego(self):
        """Verifica si el juego ha terminado"""
        if self.pos_gato == self.pos_raton:
            self.juego_terminado = True
            self.ganador = "gato"
            return True
        
        if self.turnos_transcurridos >= self.max_turnos:
            self.juego_terminado = True
            self.ganador = "raton"
            return True
        
        return False
    
    def hacer_movimiento(self, nueva_pos):
        """Realiza un movimiento en el tablero"""
        if self.turno_raton:
            self.pos_raton = nueva_pos
        else:
            self.pos_gato = nueva_pos
        
        self.turno_raton = not self.turno_raton
        if not self.turno_raton:  # Si cambió de ratón a gato, incrementar turno
            self.turnos_transcurridos += 1
        
        self.actualizar_tablero()
        self.verificar_fin_juego()
    
    def deshacer_movimiento(self, pos_anterior, turno_anterior, turnos_anterior):
        """Deshace un movimiento (para Minimax)"""
        if turno_anterior:  # Si era turno del ratón
            self.pos_raton = pos_anterior
        else:  # Si era turno del gato
            self.pos_gato = pos_anterior
        
        self.turno_raton = turno_anterior
        self.turnos_transcurridos = turnos_anterior
        self.juego_terminado = False
        self.ganador = None
        self.actualizar_tablero()

    def minimax(self, profundidad, es_maximizador, alpha=float('-inf'), beta=float('inf')):
        """Implementación del algoritmo Minimax con poda Alpha-Beta"""
        
        # Caso base: juego terminado o profundidad máxima
        if self.verificar_fin_juego() or profundidad == 0:
            return self.evaluar_posicion(), None
        
        mejor_movimiento = None
        
        if es_maximizador:  # Turno del ratón (maximizar)

            max_eval = float('-inf')
            movimientos = self.movimientos_validos(self.pos_raton, es_raton=True)
            
            for movimiento in movimientos:
                # Guardar estado actual
                pos_anterior = self.pos_raton
                turno_anterior = self.turno_raton
                turnos_anterior = self.turnos_transcurridos
                
                # Hacer movimiento
                self.hacer_movimiento(movimiento)
                
                # Llamada recursiva
                evaluacion, _ = self.minimax(profundidad - 1, False, alpha, beta)
                
                # Deshacer movimiento
                self.deshacer_movimiento(pos_anterior, turno_anterior, turnos_anterior)
                
                if evaluacion > max_eval:
                    max_eval = evaluacion
                    mejor_movimiento = movimiento
                
                alpha = max(alpha, evaluacion)
                if beta <= alpha:
                    break  # Poda Alpha-Beta
            
            return max_eval, mejor_movimiento
        
        else:  # Turno del gato (minimizar)
            min_eval = float('inf')
            movimientos = self.movimientos_validos(self.pos_gato, es_raton=False)
            
            for movimiento in movimientos:
                # Guardar estado actual
                pos_anterior = self.pos_gato
                turno_anterior = self.turno_raton
                turnos_anterior = self.turnos_transcurridos
                
                # Hacer movimiento
                self.hacer_movimiento(movimiento)
                
                # Llamada recursiva
                evaluacion, _ = self.minimax(profundidad - 1, True, alpha, beta)
                
                # Deshacer movimiento
                self.deshacer_movimiento(pos_anterior, turno_anterior, turnos_anterior)
                
                if evaluacion < min_eval:
                    min_eval = evaluacion
                    mejor_movimiento = movimiento
                
                beta = min(beta, evaluacion)
                if beta <= alpha:
                    break  # Poda Alpha-Beta
            
            return min_eval, mejor_movimiento

    def obtener_mejor_movimiento(self, profundidad=4):
        """Obtiene el mejor movimiento usando Minimax"""
        _, mejor_mov = self.minimax(profundidad, self.turno_raton)
        return mejor_mov

def main():
    print("¡Bienvenido al Laberinto del Gato y el Ratón!")
    print("=" * 10)
    print("El ratón (R) debe sobrevivir 50 turnos sin ser atrapado por el gato (G)")
    print("El ratón puede moverse en 8 direcciones, el gato solo en 4")
    print("¡Que comience la batalla épica entre instinto y estrategia!")
    print("=" * 10)
    
    # Crear el juego
    juego = LaberintoGatoRaton(6, 6)  # Tablero más pequeño para testing
    
    while not juego.juego_terminado:
        juego.mostrar_tablero()
        
        print(f"\n Calculando mejor movimiento...")
        
        # Obtener movimiento de la IA usando Minimax
        mejor_movimiento = juego.obtener_mejor_movimiento(profundidad=3)
        
        if mejor_movimiento:
            jugador = "Ratón" if juego.turno_raton else "Gato"
            print(f" {jugador} se mueve a: {mejor_movimiento}")
            juego.hacer_movimiento(mejor_movimiento)
        
        # Pausa para ver los movimientos
        input("Presiona Enter para continuar...")
    
    # Mostrar resultado final
    juego.mostrar_tablero()
    print("\n" + "="*10)
    if juego.ganador == "gato":
        print(" ¡El GATO ha ganado! ¡Atrapó al ratón!")
        print("La fría lógica matemática triunfó sobre la agilidad.")
    else:
        print("¡El RATÓN ha sobrevivido! ¡Logró escapar!")
        print("¡La velocidad y astucia vencieron al cálculo!")
    
    print("="*10)
    print(" Tu código cuenta la historia. Y el laberinto te espera. ")

if __name__ == "__main__":
    main()