"""Mission system models for Age of Voyage."""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class MissionCategory(models.Model):
    """Categories for different types of missions."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    color = models.CharField(max_length=7, help_text="Hex color code")
    
    class Meta:
        db_table = 'missions_missioncategory'
        verbose_name = _('Mission Category')
        verbose_name_plural = _('Mission Categories')
    
    def __str__(self):
        return self.name


class Mission(models.Model):
    """Base mission template."""
    
    MISSION_TYPES = [
        ('story', 'Story Mission'),
        ('side', 'Side Mission'),
        ('daily', 'Daily Mission'),
        ('contract', 'Contract Mission'),
        ('exploration', 'Exploration Mission'),
        ('combat', 'Combat Mission'),
        ('trade', 'Trade Mission'),
    ]
    
    DIFFICULTY_LEVELS = [
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Hard'),
        (4, 'Expert'),
        (5, 'Legendary'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(MissionCategory, on_delete=models.CASCADE, related_name='missions')
    mission_type = models.CharField(max_length=20, choices=MISSION_TYPES)
    difficulty = models.PositiveIntegerField(choices=DIFFICULTY_LEVELS)
    
    # Requirements
    required_level = models.PositiveIntegerField(default=1)
    required_regions = models.ManyToManyField(
        'exploration.Region',
        blank=True,
        help_text="Regions that must be discovered"
    )
    required_ships = models.JSONField(
        default=list,
        help_text="Required ship types"
    )
    required_reputation = models.JSONField(
        default=dict,
        help_text="Required faction reputations"
    )
    prerequisite_missions = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        help_text="Missions that must be completed first"
    )
    
    # Objectives
    objectives = models.JSONField(
        default=list,
        help_text="List of mission objectives"
    )
    
    # Rewards
    experience_reward = models.PositiveIntegerField()
    gold_reward = models.PositiveIntegerField(default=0)
    resource_rewards = models.JSONField(
        default=dict,
        help_text="Resource type and quantity rewards"
    )
    reputation_rewards = models.JSONField(
        default=dict,
        help_text="Faction reputation changes"
    )
    special_rewards = models.JSONField(
        default=list,
        help_text="Special items, ships, or unlocks"
    )
    
    # Time constraints
    time_limit = models.DurationField(
        null=True,
        blank=True,
        help_text="Time limit for mission completion"
    )
    
    # Availability
    is_active = models.BooleanField(default=True)
    is_repeatable = models.BooleanField(default=False)
    max_completions = models.PositiveIntegerField(
        default=1,
        help_text="Maximum times a player can complete this mission"
    )
    
    # Location
    start_region = models.ForeignKey(
        'exploration.Region',
        on_delete=models.CASCADE,
        related_name='starting_missions'
    )
    
    class Meta:
        db_table = 'missions_mission'
        verbose_name = _('Mission')
        verbose_name_plural = _('Missions')
    
    def __str__(self):
        return self.title


class PlayerMission(models.Model):
    """Player's progress on specific missions."""
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('abandoned', 'Abandoned'),
    ]
    
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='missions')
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='player_missions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Progress tracking
    objectives_completed = models.JSONField(
        default=dict,
        help_text="Track completion status of each objective"
    )
    progress_data = models.JSONField(
        default=dict,
        help_text="Store mission-specific progress data"
    )
    
    # Timestamps
    discovered_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    
    # Completion tracking
    completion_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'missions_playermission'
        unique_together = ['player', 'mission']
        verbose_name = _('Player Mission')
        verbose_name_plural = _('Player Missions')
    
    def __str__(self):
        return f"{self.player.captain_name} - {self.mission.title} ({self.status})"
    
    @property
    def is_completed(self):
        """Check if mission is completed."""
        return self.status == 'completed'
    
    @property
    def is_expired(self):
        """Check if mission has expired."""
        if self.deadline:
            from django.utils import timezone
            return timezone.now() > self.deadline
        return False
    
    @property
    def completion_percentage(self):
        """Calculate completion percentage."""
        if not self.objectives_completed:
            return 0
        
        total_objectives = len(self.mission.objectives)
        completed_objectives = sum(1 for completed in self.objectives_completed.values() if completed)
        
        return (completed_objectives / total_objectives * 100) if total_objectives > 0 else 0


class MissionObjective(models.Model):
    """Individual objectives within missions."""
    
    OBJECTIVE_TYPES = [
        ('go_to', 'Go to Location'),
        ('defeat', 'Defeat Enemies'),
        ('collect', 'Collect Items'),
        ('deliver', 'Deliver Items'),
        ('trade', 'Complete Trade'),
        ('discover', 'Discover Location'),
        ('survive', 'Survive Duration'),
        ('escort', 'Escort NPC'),
    ]
    
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='objective_details')
    title = models.CharField(max_length=200)
    description = models.TextField()
    objective_type = models.CharField(max_length=20, choices=OBJECTIVE_TYPES)
    order = models.PositiveIntegerField(default=1)
    
    # Objective parameters
    target_region = models.ForeignKey(
        'exploration.Region',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    target_quantity = models.PositiveIntegerField(default=1)
    target_data = models.JSONField(
        default=dict,
        help_text="Additional objective-specific data"
    )
    
    # Optional objective
    is_optional = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'missions_missionobjective'
        unique_together = ['mission', 'order']
        verbose_name = _('Mission Objective')
        verbose_name_plural = _('Mission Objectives')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.mission.title} - {self.title}"


class MissionReward(models.Model):
    """Detailed mission rewards."""
    
    REWARD_TYPES = [
        ('experience', 'Experience Points'),
        ('gold', 'Gold'),
        ('resource', 'Resources'),
        ('item', 'Special Item'),
        ('ship', 'Ship'),
        ('unlock', 'Feature Unlock'),
        ('reputation', 'Faction Reputation'),
    ]
    
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='reward_details')
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    
    # Conditional rewards
    requires_optional_objectives = models.BooleanField(default=False)
    bonus_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.0,
        help_text="Multiplier for bonus conditions"
    )
    
    class Meta:
        db_table = 'missions_missionreward'
        verbose_name = _('Mission Reward')
        verbose_name_plural = _('Mission Rewards')
    
    def __str__(self):
        return f"{self.mission.title} - {self.name} ({self.quantity})"


class QuestGiver(models.Model):
    """NPCs or entities that give missions."""
    
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    
    # Location
    region = models.ForeignKey('exploration.Region', on_delete=models.CASCADE, related_name='quest_givers')
    
    # Appearance
    portrait = models.ImageField(upload_to='quest_givers/', blank=True, null=True)
    
    # Faction affiliation
    faction = models.ForeignKey(
        'players.Faction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quest_givers'
    )
    
    # Requirements to interact
    required_reputation = models.IntegerField(default=0)
    required_level = models.PositiveIntegerField(default=1)
    
    # Missions offered
    missions = models.ManyToManyField(Mission, through='QuestGiverMission')
    
    class Meta:
        db_table = 'missions_questgiver'
        verbose_name = _('Quest Giver')
        verbose_name_plural = _('Quest Givers')
    
    def __str__(self):
        return f"{self.name} - {self.title}" if self.title else self.name


class QuestGiverMission(models.Model):
    """Relationship between quest givers and their missions."""
    
    quest_giver = models.ForeignKey(QuestGiver, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    
    # Availability conditions
    unlock_level = models.PositiveIntegerField(default=1)
    unlock_reputation = models.IntegerField(default=0)
    prerequisite_missions = models.ManyToManyField(
        Mission,
        blank=True,
        related_name='unlocks_missions'
    )
    
    class Meta:
        db_table = 'missions_questgivermission'
        unique_together = ['quest_giver', 'mission']
        verbose_name = _('Quest Giver Mission')
        verbose_name_plural = _('Quest Giver Missions')
    
    def __str__(self):
        return f"{self.quest_giver.name} offers {self.mission.title}"
