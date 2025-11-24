"""
Módulo para gerenciar calendário de negociação, incluindo feriados e dias úteis.
"""
from datetime import date, datetime, timedelta
from typing import List, Set, Optional
import pandas as pd
import pandas_market_calendars as mcal
import logging

logger = logging.getLogger(__name__)

class TradingCalendar:
    """
    Classe para gerenciar calendário de negociação, incluindo feriados e dias úteis.
    
    Esta classe utiliza o pacote pandas_market_calendars para obter os dias de negociação
    da B3 (Bolsa de Valores do Brasil) e adiciona lógica para lidar com feriados móveis
    e outros feriados específicos do mercado brasileiro.
    """
    
    def __init__(self, market: str = 'B3'):
        """
        Inicializa o calendário para um mercado específico.
        
        Args:
            market: Código do mercado (padrão: 'B3' para Bolsa de Valores do Brasil)
        """
        self.market = market
        self._holidays: Set[date] = set()
        self._load_holidays()
    
    def _load_holidays(self) -> None:
        """Carrega os feriados do mercado especificado."""
        try:
            # Usa o pandas_market_calendars para obter os feriados da B3
            b3 = mcal.get_calendar('B3')
            
            # Obtém os feriados para os próximos 5 anos
            end_date = (datetime.now() + timedelta(days=365*5)).strftime('%Y-%m-%d')
            schedule = b3.schedule(start_date='2000-01-01', end_date=end_date)
            
            # Converte para um conjunto de datas
            trading_days = set(schedule.index.date)
            
            # Gera todos os dias no período e marca os não-úteis como feriados
            all_days = pd.date_range(start='2000-01-01', end=end_date).date
            self._holidays = {
                day for day in all_days 
                if day.weekday() < 5 and  # Apenas dias da semana
                day not in trading_days   # Que não são dias de negociação
            }
            
            # Adiciona feriados móveis que possam ter sido perdidos
            self._add_moving_holidays()
            
            logger.info(f"Calendário de negociação carregado com {len(self._holidays)} feriados/dias não úteis")
            
        except Exception as e:
            logger.error(f"Erro ao carregar calendário de negociação: {e}")
            # Fallback para feriados fixos do Brasil em caso de erro
            self._set_default_holidays()
    
    def _add_moving_holidays(self) -> None:
        """Adiciona feriados móveis que podem não estar no calendário da B3."""
        current_year = datetime.now().year
        years = range(current_year - 2, current_year + 3)  # +/- 2 anos do atual
        
        for year in years:
            # Sexta-feira Santa (2 dias antes do Domingo de Páscoa)
            easter_sunday = self._calculate_easter_sunday(year)
            good_friday = easter_sunday - timedelta(days=2)
            self._holidays.add(good_friday.date())
            
            # Corpus Christi (60 dias após a Páscoa)
            corpus_christi = easter_sunday + timedelta(days=60)
            self._holidays.add(corpus_christi.date())
    
    @staticmethod
    def _calculate_easter_sunday(year: int) -> datetime:
        """Calcula o Domingo de Páscoa usando o algoritmo de Meeus/Jones/Butcher."""
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        
        return datetime(year, month, day)
    
    def _set_default_holidays(self) -> None:
        """Define feriados fixos do Brasil como fallback."""
        current_year = datetime.now().year
        years = range(current_year - 2, current_year + 3)  # +/- 2 anos do atual
        
        for year in years:
            # Feriados nacionais fixos
            fixed_holidays = [
                date(year, 1, 1),    # Ano Novo
                date(year, 4, 21),   # Tiradentes
                date(year, 5, 1),    # Dia do Trabalhador
                date(year, 9, 7),    # Independência do Brasil
                date(year, 10, 12),  # Nossa Senhora Aparecida
                date(year, 11, 2),   # Finados
                date(year, 11, 15),  # Proclamação da República
                date(year, 12, 25),  # Natal
            ]
            
            for holiday in fixed_holidays:
                self._holidays.add(holiday)
    
    def is_trading_day(self, date_obj: date) -> bool:
        """
        Verifica se uma data é um dia de negociação (dia útil e não feriado).
        
        Args:
            date_obj: Data a ser verificada (objeto date ou datetime)
            
        Returns:
            bool: True se for dia de negociação, False caso contrário
        """
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
            
        # Verifica se é final de semana
        if date_obj.weekday() >= 5:  # 5 = sábado, 6 = domingo
            return False
            
        # Verifica se é feriado
        return date_obj not in self._holidays
    
    def get_trading_days(self, start_date: date, end_date: date) -> List[date]:
        """
        Retorna uma lista de dias úteis entre duas datas.
        
        Args:
            start_date: Data inicial (inclusiva)
            end_date: Data final (inclusiva)
            
        Returns:
            List[date]: Lista de dias úteis no intervalo
        """
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()
            
        all_days = pd.date_range(start=start_date, end=end_date).date
        return [day for day in all_days if self.is_trading_day(day)]
    
    def get_previous_trading_day(self, date_obj: date) -> date:
        """
        Retorna o dia útil anterior à data fornecida.
        
        Args:
            date_obj: Data de referência
            
        Returns:
            date: Último dia útil anterior
        """
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
            
        prev_day = date_obj - timedelta(days=1)
        while not self.is_trading_day(prev_day):
            prev_day -= timedelta(days=1)
            
        return prev_day
    
    def get_next_trading_day(self, date_obj: date) -> date:
        """
        Retorna o próximo dia útil após a data fornecida.
        
        Args:
            date_obj: Data de referência
            
        Returns:
            date: Próximo dia útil
        """
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
            
        next_day = date_obj + timedelta(days=1)
        while not self.is_trading_day(next_day):
            next_day += timedelta(days=1)
            
        return next_day

# Instância global para uso em todo o sistema
# This global instance ensures that the trading calendar is initialized once
# and can be reused across different parts of the application, avoiding
# redundant loading of holiday data.
trading_calendar = TradingCalendar()
