"""Trade and commerce models for Age of Voyage."""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class Commodity(models.Model):
    """Tradeable goods and resources."""
    
    COMMODITY_CATEGORIES = [
        ('basic', 'Basic Resources'),
        ('luxury', 'Luxury Goods'),
        ('military', 'Military Supplies'),
        ('food', 'Food & Provisions'),
        ('craft', 'Crafted Goods'),
        ('exotic', 'Exotic Items'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=COMMODITY_CATEGORIES)
    description = models.TextField()
    
    # Base economic data
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    weight_per_unit = models.PositiveIntegerField(default=1)
    
    # Market dynamics
    demand_volatility = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=1.0,
        help_text="How much prices fluctuate (1.0 = normal, higher = more volatile)"
    )
    
    # Regional preferences
    preferred_regions = models.ManyToManyField(
        'exploration.WorldRegion',
        blank=True,
        help_text="Regions where this commodity is in higher demand"
    )
    
    # Visual
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    image = models.ImageField(upload_to='commodities/', blank=True, null=True)
    
    class Meta:
        db_table = 'trade_commodity'
        verbose_name = _('Commodity')
        verbose_name_plural = _('Commodities')
    
    def __str__(self):
        return self.name


class Market(models.Model):
    """Markets in different regions where trading occurs."""
    
    region = models.OneToOneField(
        'exploration.Region',
        on_delete=models.CASCADE,
        related_name='market'
    )
    
    # Market characteristics
    prosperity_level = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Economic prosperity level affecting prices and availability"
    )
    trade_volume = models.PositiveIntegerField(
        default=100,
        help_text="Daily trade volume affecting price stability"
    )
    
    # Market conditions
    is_active = models.BooleanField(default=True)
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.05'),
        help_text="Tax rate as decimal (0.05 = 5%)"
    )
    
    # Specializations
    specialized_commodities = models.ManyToManyField(
        Commodity,
        blank=True,
        help_text="Commodities this market specializes in"
    )
    
    class Meta:
        db_table = 'trade_market'
        verbose_name = _('Market')
        verbose_name_plural = _('Markets')
    
    def __str__(self):
        return f"{self.region.name} Market"


class MarketPrice(models.Model):
    """Current prices for commodities in specific markets."""
    
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='prices')
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, related_name='market_prices')
    
    # Pricing
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Supply and demand
    supply = models.PositiveIntegerField(default=100)
    demand = models.PositiveIntegerField(default=100)
    
    # Market dynamics
    price_trend = models.CharField(
        max_length=10,
        choices=[
            ('rising', 'Rising'),
            ('stable', 'Stable'),
            ('falling', 'Falling'),
        ],
        default='stable'
    )
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trade_marketprice'
        unique_together = ['market', 'commodity']
        verbose_name = _('Market Price')
        verbose_name_plural = _('Market Prices')
    
    def __str__(self):
        return f"{self.commodity.name} at {self.market.region.name}: {self.current_price}"
    
    def update_price(self, supply_change=0, demand_change=0):
        """Update price based on supply and demand changes."""
        self.supply = max(0, self.supply + supply_change)
        self.demand = max(0, self.demand + demand_change)
        
        # Calculate new price based on supply/demand ratio
        if self.demand > 0:
            ratio = self.supply / self.demand
            price_modifier = 1 / ratio if ratio > 0 else 2.0
            
            # Apply volatility
            price_modifier *= float(self.commodity.demand_volatility)
            
            # Calculate new price
            new_price = float(self.commodity.base_price) * price_modifier
            self.current_price = Decimal(str(round(new_price, 2)))
            
            # Update buy/sell prices with market spread
            spread = self.current_price * Decimal('0.1')  # 10% spread
            self.buy_price = max(Decimal('0.01'), self.current_price - spread)
            self.sell_price = self.current_price + spread
            
            # Update trend
            if price_modifier > 1.1:
                self.price_trend = 'rising'
            elif price_modifier < 0.9:
                self.price_trend = 'falling'
            else:
                self.price_trend = 'stable'
        
        self.save()


class TradeRoute(models.Model):
    """Established trade routes between markets."""
    
    from_market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='routes_from')
    to_market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='routes_to')
    
    # Route characteristics
    distance = models.PositiveIntegerField(help_text="Distance in nautical miles")
    established_at = models.DateTimeField(auto_now_add=True)
    popularity = models.PositiveIntegerField(default=1, help_text="How popular this route is with traders")
    
    # Profitability
    average_profit_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.0'),
        help_text="Average profit margin as percentage"
    )
    
    class Meta:
        db_table = 'trade_traderoute'
        unique_together = ['from_market', 'to_market']
        verbose_name = _('Trade Route')
        verbose_name_plural = _('Trade Routes')
    
    def __str__(self):
        return f"{self.from_market.region.name} → {self.to_market.region.name}"


class TradeContract(models.Model):
    """Special trading contracts with specific terms."""
    
    CONTRACT_TYPES = [
        ('delivery', 'Delivery Contract'),
        ('supply', 'Supply Contract'),
        ('exclusive', 'Exclusive Deal'),
        ('bulk', 'Bulk Order'),
    ]
    
    CONTRACT_STATUS = [
        ('available', 'Available'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES)
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS, default='available')
    
    # Contract details
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Locations
    pickup_market = models.ForeignKey(
        Market,
        on_delete=models.CASCADE,
        related_name='pickup_contracts'
    )
    delivery_market = models.ForeignKey(
        Market,
        on_delete=models.CASCADE,
        related_name='delivery_contracts'
    )
    
    # Terms
    deadline = models.DateTimeField()
    bonus_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Requirements
    required_level = models.PositiveIntegerField(default=1)
    required_reputation = models.IntegerField(default=0)
    
    # Assignment
    assigned_player = models.ForeignKey(
        'players.Player',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trade_contracts'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'trade_tradecontract'
        verbose_name = _('Trade Contract')
        verbose_name_plural = _('Trade Contracts')
    
    def __str__(self):
        return self.title
    
    @property
    def total_value(self):
        """Calculate total contract value."""
        return self.quantity * self.price_per_unit + self.bonus_payment
    
    @property
    def is_expired(self):
        """Check if contract has expired."""
        from django.utils import timezone
        return timezone.now() > self.deadline


class TradeTransaction(models.Model):
    """Record of completed trades."""
    
    TRANSACTION_TYPES = [
        ('buy', 'Purchase'),
        ('sell', 'Sale'),
        ('contract', 'Contract Fulfillment'),
    ]
    
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='trade_transactions')
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='transactions')
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=12, decimal_places=2)
    tax_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Associated contract (if any)
    contract = models.ForeignKey(
        TradeContract,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'trade_tradetransaction'
        verbose_name = _('Trade Transaction')
        verbose_name_plural = _('Trade Transactions')
    
    def __str__(self):
        return f"{self.player.captain_name} - {self.transaction_type} {self.quantity} {self.commodity.name}"
    
    def save(self, *args, **kwargs):
        """Calculate total value and tax when saving."""
        self.total_value = self.quantity * self.price_per_unit
        self.tax_paid = self.total_value * self.market.tax_rate
        super().save(*args, **kwargs)


class PlayerTradeReputation(models.Model):
    """Player reputation with different markets/regions."""
    
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='trade_reputations')
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='player_reputations')
    
    reputation = models.IntegerField(
        default=0,
        validators=[MinValueValidator(-100), MaxValueValidator(100)],
        help_text="Trade reputation from -100 to +100"
    )
    
    # Trading statistics
    total_trades = models.PositiveIntegerField(default=0)
    total_value_traded = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    contracts_completed = models.PositiveIntegerField(default=0)
    contracts_failed = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'trade_playertradereputation'
        unique_together = ['player', 'market']
        verbose_name = _('Player Trade Reputation')
        verbose_name_plural = _('Player Trade Reputations')
    
    def __str__(self):
        return f"{self.player.captain_name} - {self.market.region.name}: {self.reputation}"
    
    @property
    def reputation_status(self):
        """Get reputation status as string."""
        if self.reputation >= 75:
            return "Trusted Partner"
        elif self.reputation >= 25:
            return "Valued Trader"
        elif self.reputation >= -25:
            return "Regular Customer"
        elif self.reputation >= -75:
            return "Suspicious"
        else:
            return "Banned"
